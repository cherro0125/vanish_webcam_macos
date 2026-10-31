import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch

import numpy as np

from local_app import vanish_cam as app
from local_app.live_background import LiveBackground
from local_app.test_video_output import arguments


H, W = 48, 80


def room() -> np.ndarray:
    y, x = np.mgrid[0:H, 0:W]
    return np.dstack([x * 3, y * 4, 60 + (x + y) % 50]).astype(np.uint8)


def person_mask(left=30, right=50) -> np.ndarray:
    mask = np.zeros((H, W), np.float32)
    mask[8:, left:right] = 1.0
    return mask


def with_person(scene: np.ndarray, mask: np.ndarray) -> np.ndarray:
    frame = scene.copy()
    frame[mask > 0.5] = (30, 40, 220)
    return frame


class LiveBackgroundModelTests(unittest.TestCase):
    def test_person_is_replaced_by_the_room_behind_them(self):
        live = LiveBackground()
        live.seed(room())
        mask = person_mask()
        for _ in range(10):
            cover = live.update(with_person(room(), mask), mask)
        output = live.compose(with_person(room(), mask), cover)
        np.testing.assert_allclose(output.astype(int), room().astype(int), atol=1)

    def test_moved_objects_are_learned_without_recapturing(self):
        live = LiveBackground()
        live.seed(room())
        changed = room()
        changed[5:20, 2:12] = (0, 200, 0)  # A new object away from the person.
        mask = person_mask()
        for _ in range(30):
            live.update(with_person(changed, mask), mask)
        np.testing.assert_allclose(live.model[5:20, 2:12], np.full((15, 10, 3), (0, 200, 0)), atol=2)

    def test_light_change_also_reaches_the_area_behind_the_person(self):
        live = LiveBackground()
        live.seed(room())
        brighter = np.clip(room().astype(np.float32) * 1.3, 0, 255).astype(np.uint8)
        mask = person_mask()
        for _ in range(40):
            cover = live.update(with_person(brighter, mask), mask)
        output = live.compose(with_person(brighter, mask), cover)
        hidden = mask > 0.5
        error = np.abs(output[hidden].astype(int) - brighter[hidden].astype(int)).mean()
        stale = np.abs(room()[hidden].astype(int) - brighter[hidden].astype(int)).mean()
        self.assertLess(error, stale * 0.2)

    def test_newly_revealed_pixels_are_taken_immediately(self):
        live = LiveBackground(fill_unseen=True)
        mask = person_mask()
        live.update(with_person(room(), mask), mask)  # Starts with the person in frame.
        self.assertFalse(live.known[mask > 0.5].any())
        nobody = np.zeros((H, W), np.float32)
        live.update(room(), nobody)
        self.assertTrue(live.known.all())
        np.testing.assert_array_equal(live.model.astype(np.uint8), room())

    def test_fill_unseen_paints_never_seen_area_from_surroundings(self):
        wall = np.full((H, W, 3), (120, 140, 160), np.uint8)
        mask = person_mask()
        frame = with_person(wall, mask)
        live = LiveBackground(fill_unseen=True)
        cover = live.update(frame, mask)
        output = live.compose(frame, cover)
        np.testing.assert_allclose(output[mask > 0.5].astype(int),
                                   np.broadcast_to((120, 140, 160), (int((mask > 0.5).sum()), 3)), atol=6)

    def test_without_fill_unseen_never_seen_area_is_not_invented(self):
        mask = person_mask()
        live = LiveBackground(fill_unseen=False)
        frame = with_person(room(), mask)
        live.update(frame, mask)
        np.testing.assert_array_equal(live.model[mask > 0.5].astype(np.uint8), frame[mask > 0.5])


class FakeClock:
    """perf_counter() returns the time of the frame currently being processed."""

    def __init__(self, frames):
        self.frames = list(frames)
        self.now = 0.0

    def read(self):
        self.now, frame = self.frames.pop(0)
        return True, frame

    def __call__(self):
        return self.now


class LiveLoopTests(unittest.TestCase):
    def run_loop(self, frames, keys, recognizer=None, **options):
        clock = FakeClock(frames)
        capture = Mock()
        capture.read.side_effect = clock.read
        shown = []
        mask_calls = []

        def fake_mask(segmenter, image, timestamp_ms, width, height):
            mask_calls.append(timestamp_ms)
            frame = image.numpy_view()
            return np.all(frame == (220, 40, 30), axis=2).astype(np.float32)  # RGB person.

        with ExitStack() as mocks:
            mocks.enter_context(patch.object(app, "parse_args", return_value=arguments(**options)))
            mocks.enter_context(patch.object(app, "download_models"))
            mocks.enter_context(patch.object(app, "open_camera", return_value=capture))
            mocks.enter_context(patch.object(app, "create_tasks",
                                              return_value=(Mock(), recognizer or Mock())))
            mocks.enter_context(patch.object(app, "VanishSound"))
            mocks.enter_context(patch.object(app, "open_virtual_camera", return_value=None))
            mocks.enter_context(patch.object(app, "person_mask", side_effect=fake_mask))
            mocks.enter_context(patch.object(app, "recognize_gesture", return_value=("No_Hand", 0.0)))
            mocks.enter_context(patch.object(app.time, "perf_counter", side_effect=clock))
            for name in ("namedWindow", "resizeWindow", "destroyAllWindows"):
                mocks.enter_context(patch.object(app.cv2, name))
            mocks.enter_context(patch.object(app.cv2, "imshow",
                                              side_effect=lambda name, frame: shown.append(frame.copy())))
            mocks.enter_context(patch.object(app.cv2, "waitKey", side_effect=keys))
            mocks.enter_context(patch("builtins.print"))
            self.assertEqual(app.run(), 0)
        return shown, mask_calls

    def test_after_vanishing_the_room_stays_live(self):
        mask = person_mask()
        lamp_on = room()
        lamp_on[2:10, 2:10] = (255, 255, 255)
        frames = [
            (0.1, room()), (3.6, room()), (4.1, room()),          # Calibration.
            (4.3, with_person(room(), mask)),                     # Ready, V pressed.
            (4.5, with_person(room(), mask)),                     # Dissolving.
            (8.2, with_person(room(), mask)),                     # Vanished.
            (8.4, with_person(lamp_on, mask)),                    # Lamp switched on.
            (8.6, with_person(lamp_on, mask)),
        ]
        keys = [0, 0, 0, ord("v"), 0, 0, 0, ord("q")]
        shown, _ = self.run_loop(frames, keys, live_background=True)
        np.testing.assert_allclose(shown[5].astype(int), room().astype(int), atol=1)
        last = shown[7]
        np.testing.assert_allclose(last[2:10, 2:10], np.full((8, 8, 3), 255), atol=2)  # Live change shown.
        np.testing.assert_allclose(last[mask > 0.5].astype(int), room()[mask > 0.5].astype(int), atol=1)

    def test_naruto_log_stays_on_a_live_room(self):
        mask = person_mask()
        lamp_on = room()
        lamp_on[2:10, 2:10] = (255, 255, 255)
        recognizer = Mock()
        recognizer.recognize_joined_hands.return_value = True
        frames = [
            (0.1, room()), (3.6, room()), (4.1, room()),          # Calibration.
            (4.3, with_person(room(), mask)),                     # Hands joined.
            (4.4, with_person(room(), mask)),                     # Smoke.
            (6.0, with_person(room(), mask)),                     # Log landed.
            (6.2, with_person(lamp_on, mask)),                    # Lamp switched on.
        ]
        shown, _ = self.run_loop(frames, [0] * 6 + [ord("q")], recognizer=recognizer,
                                 mode="naruto", live_background=True)
        log_only = shown[5].astype(int) - room().astype(int)
        self.assertTrue(np.any(log_only != 0))  # The log is drawn.
        np.testing.assert_allclose(shown[6][2:10, 2:10], np.full((8, 8, 3), 255), atol=2)
        self.assertFalse(np.any(np.all(shown[6] == (30, 40, 220), axis=2)))  # Person hidden.

    def test_fill_unseen_starts_without_calibration(self):
        wall = np.full((H, W, 3), (120, 140, 160), np.uint8)
        mask = person_mask()
        frames = [
            (0.1, with_person(wall, mask)),   # Ready at once, V pressed.
            (0.2, with_person(wall, mask)),
            (4.0, with_person(wall, mask)),   # Vanished: never-seen area painted in.
        ]
        shown, mask_calls = self.run_loop(frames, [ord("v"), 0, ord("q")], fill_unseen=True)
        np.testing.assert_array_equal(shown[0], frames[0][1])  # No calibration pause.
        self.assertTrue(mask_calls)
        hidden = shown[2][mask > 0.5].astype(int)
        np.testing.assert_allclose(hidden, np.broadcast_to((120, 140, 160), hidden.shape), atol=6)

    def test_classic_mode_is_unchanged(self):
        frames = [(0.1, room()), (3.6, room()), (4.1, room()), (4.3, room())]
        shown, mask_calls = self.run_loop(frames, [0, 0, 0, ord("q")])
        self.assertEqual(mask_calls, [])  # No segmentation before a vanish starts.
        self.assertEqual(len(shown), 4)


if __name__ == "__main__":
    unittest.main()
