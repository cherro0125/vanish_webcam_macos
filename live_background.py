"""Background plate that keeps learning while the person is in the frame.

The classic mode freezes one clean photo of the room. This model instead
refreshes every pixel the person does not cover, so moved objects and light
changes show up on their own. Pixels hidden behind the person keep their last
seen value, corrected by the light change measured on the visible pixels.
Areas the camera has never seen can optionally be painted in from their
surroundings (``fill_unseen``).
"""

from __future__ import annotations

import cv2
import numpy as np


class LiveBackground:
    # Share of a revealed pixel's colour that is blended into the model per
    # update (updates run at 10-20 Hz, so changes settle in well under a second).
    RATE = 0.2
    # Extra margin around the silhouette, as a share of the frame's long side:
    # hides segmentation lag and hair the model misses.
    MARGIN = 0.025
    # Pixels whose coverage is below this count as clearly visible.
    VISIBLE = 0.05
    # Unseen areas are painted at this fraction of the frame size: much faster
    # and the result is a soft fill either way.
    FILL_SCALE = 0.25
    # The painted fill is only a soft guess, so it is refreshed every few
    # model updates instead of every frame.
    FILL_EVERY = 4

    def __init__(self, fill_unseen: bool = False):
        self.fill_unseen = fill_unseen
        self.model: np.ndarray | None = None  # float32 HxWx3, BGR
        self.known: np.ndarray | None = None  # bool HxW, seen without the person
        self._fill_age = self.FILL_EVERY  # paint on the first update

    @property
    def ready(self) -> bool:
        return self.model is not None

    def reset(self) -> None:
        self.model = None
        self.known = None
        self._fill_age = self.FILL_EVERY

    def seed(self, background: np.ndarray) -> None:
        """Start from a clean plate captured with nobody in the frame."""
        self.model = background.astype(np.float32)
        self.known = np.ones(background.shape[:2], dtype=bool)
        self._fill_age = self.FILL_EVERY

    def coverage(self, mask: np.ndarray) -> np.ndarray:
        """Soft 0..1 map of the area to replace: silhouette plus a safety margin.

        Computed at a quarter of the resolution (it is blurred anyway), which
        keeps the large dilation cheap enough for every frame.
        """
        height, width = mask.shape
        small_size = (max(8, width // 4), max(8, height // 4))
        small = cv2.resize(mask, small_size, interpolation=cv2.INTER_AREA)
        radius = max(2, round(max(small_size) * self.MARGIN))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius + 1, 2 * radius + 1))
        grown = cv2.dilate((small > 0.1).astype(np.uint8), kernel).astype(np.float32)
        soft = cv2.GaussianBlur(grown, (0, 0), sigmaX=radius / 2)
        soft = cv2.resize(soft, (width, height), interpolation=cv2.INTER_LINEAR)
        return np.maximum(soft, mask.astype(np.float32))

    def update(self, frame: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Learn from the uncovered pixels of ``frame``; returns the coverage map."""
        cover = self.coverage(mask)
        visible = cover < self.VISIBLE
        if self.model is None or self.model.shape != frame.shape:
            self.model = frame.astype(np.float32)
            self.known = visible.copy()
            self._fill_age = self.FILL_EVERY
            self._refresh_fill()
            return cover

        # Blending visible pixels at RATE moves them, on average, by this
        # factor; apply the same light change to the hidden ones, so the patch
        # behind the person does not end up brighter or darker than the room
        # after a lamp or the camera's auto exposure changes.
        step = 4
        reference = (visible & self.known)[::step, ::step]
        hidden_box = _bounding_box((~visible).astype(np.uint8))
        if hidden_box is not None and reference.sum() > 0.02 * reference.size:
            # Median of per-pixel ratios: a room-wide light change moves it,
            # a single new or moved object does not.
            seen_now = frame[::step, ::step][reference].astype(np.float32)
            seen_before = self.model[::step, ::step][reference]
            ratios = (seen_now + 4.0) / (seen_before + 4.0)
            gain = np.clip(np.median(ratios, axis=0), 0.5, 2.0)
            factor = (1.0 + self.RATE * (gain - 1.0)).astype(np.float32)
            if np.abs(factor - 1.0).max() > 1e-3:
                top, bottom, left, right = hidden_box
                # Visible pixels inside the box are re-learned right below.
                self.model[top:bottom, left:right] *= factor

        # Revealed pixels: blend in gradually, but take never-seen ones at once.
        learn = (visible & self.known).astype(np.uint8)
        cv2.accumulateWeighted(frame, self.model, self.RATE, mask=learn)
        newly_seen = visible & ~self.known
        if newly_seen.any():
            self.model[newly_seen] = frame[newly_seen]
            self.known |= newly_seen
        self._fill_age += 1
        self._refresh_fill()
        return cover

    def _refresh_fill(self) -> None:
        """Paint never-seen pixels from their surroundings (OpenCV inpaint).

        The result is written straight into the model: unseen pixels are never
        learned from the camera (they are replaced as soon as they are seen),
        so the painted values cannot leak into the real background.
        """
        if not self.fill_unseen or self._fill_age < self.FILL_EVERY or self.known.all():
            return
        self._fill_age = 0
        height, width = self.known.shape
        unseen = (~self.known).astype(np.uint8)
        top, bottom, left, right = _bounding_box(unseen, pad=max(height, width) // 16)
        region = self.model[top:bottom, left:right]
        region_unseen = unseen[top:bottom, left:right]
        small_size = (max(8, round((right - left) * self.FILL_SCALE)),
                      max(8, round((bottom - top) * self.FILL_SCALE)))
        small = np.clip(cv2.resize(region, small_size, interpolation=cv2.INTER_AREA), 0, 255)
        small_unseen = cv2.resize(region_unseen, small_size, interpolation=cv2.INTER_NEAREST)
        small_unseen = cv2.dilate(small_unseen, np.ones((3, 3), np.uint8))
        painted = cv2.inpaint(small.astype(np.uint8), small_unseen, 3, cv2.INPAINT_TELEA)
        painted = cv2.resize(painted, (right - left, bottom - top), interpolation=cv2.INTER_LINEAR)
        hole = region_unseen.astype(bool)
        region[hole] = painted[hole]

    def compose(self, frame: np.ndarray, cover: np.ndarray) -> np.ndarray:
        """Live frame with the covered area replaced by the learned background."""
        output = frame.copy()
        box = _bounding_box((cover > 1e-3).astype(np.uint8))
        if box is None:
            return output
        top, bottom, left, right = box
        alpha = np.ascontiguousarray(cover[top:bottom, left:right])
        blended = cv2.blendLinear(
            self.model[top:bottom, left:right],
            frame[top:bottom, left:right].astype(np.float32),
            alpha, 1.0 - alpha,
        )
        output[top:bottom, left:right] = cv2.convertScaleAbs(blended)
        return output


def _bounding_box(mask: np.ndarray, pad: int = 0) -> tuple[int, int, int, int] | None:
    """(top, bottom, left, right) of the non-zero pixels, or None if empty."""
    points = cv2.findNonZero(mask)
    if points is None:
        return None
    x, y, width, height = cv2.boundingRect(points)
    rows, cols = mask.shape[:2]
    return (max(0, y - pad), min(rows, y + height + pad),
            max(0, x - pad), min(cols, x + width + pad))
