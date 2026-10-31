import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np

from local_app import vanish_cam as app
from local_app import vanish_sound


def fake_capture(opened=True, frames=()):
    capture = Mock()
    capture.isOpened.return_value = opened
    capture.read.side_effect = list(frames) or [(False, None)] * 1000
    return capture


class CameraBackendTests(unittest.TestCase):
    def test_macos_prefers_avfoundation(self):
        with patch.object(app.platform, "system", return_value="Darwin"):
            self.assertEqual(app.camera_backends()[0], app.cv2.CAP_AVFOUNDATION)
        with patch.object(app.platform, "system", return_value="Windows"):
            self.assertEqual(app.camera_backends()[0], app.cv2.CAP_DSHOW)

    def test_waits_for_first_frame_after_empty_reads(self):
        frame = np.zeros((4, 4, 3), np.uint8)
        capture = fake_capture(frames=[(False, None), (True, None), (True, frame)])
        with patch.object(app.time, "sleep"):
            self.assertTrue(app.wait_for_first_frame(capture, timeout=5))
        self.assertEqual(capture.read.call_count, 3)

    def test_falls_back_to_next_backend_when_no_frames(self):
        frame = np.zeros((4, 4, 3), np.uint8)
        silent = fake_capture()
        working = fake_capture(frames=[(True, frame)])
        with ExitStack() as mocks:
            mocks.enter_context(patch.object(app.platform, "system", return_value="Darwin"))
            video = mocks.enter_context(
                patch.object(app.cv2, "VideoCapture", side_effect=[silent, working])
            )
            mocks.enter_context(patch.object(app, "wait_for_first_frame",
                                              side_effect=[False, True]))
            self.assertIs(app.open_camera(0, 640, 480), working)
        self.assertEqual([c.args[1] for c in video.call_args_list],
                         [app.cv2.CAP_AVFOUNDATION, app.cv2.CAP_ANY])
        silent.release.assert_called_once()
        working.release.assert_not_called()

    def test_macos_error_mentions_camera_permission(self):
        with ExitStack() as mocks:
            mocks.enter_context(patch.object(app.platform, "system", return_value="Darwin"))
            mocks.enter_context(patch.object(app.cv2, "VideoCapture",
                                              side_effect=lambda *a: fake_capture(opened=False)))
            with self.assertRaisesRegex(RuntimeError, "Privacy e sicurezza"):
                app.open_camera(0, 640, 480)


class MenuVisibilityTests(unittest.TestCase):
    def run_menu(self, visibility, keys):
        with ExitStack() as mocks:
            for name in ("namedWindow", "setMouseCallback", "imshow", "destroyWindow"):
                mocks.enter_context(patch.object(app.cv2, name))
            mocks.enter_context(patch.object(app.cv2, "getWindowProperty", side_effect=visibility))
            mocks.enter_context(patch.object(app.cv2, "waitKey", side_effect=keys))
            return app.choose_mode()

    def test_window_not_yet_visible_does_not_close_menu(self):
        self.assertEqual(self.run_menu([-1, 0, 1], [0, 0, ord("1")]), "normal")

    def test_closing_a_visible_window_cancels(self):
        self.assertIsNone(self.run_menu([1, 0], [0, 0]))


class SoundFallbackTests(unittest.TestCase):
    def test_afplay_used_on_macos_without_ffplay(self):
        path = Path("/tmp/vanish.MP3")
        which = {"afplay": "/usr/bin/afplay"}.get
        with patch.object(vanish_sound.shutil, "which", side_effect=which), \
                patch.object(vanish_sound.sys, "platform", "darwin"):
            self.assertEqual(vanish_sound.external_player(path), ["/usr/bin/afplay", str(path)])
        with patch.object(vanish_sound.shutil, "which", side_effect=which), \
                patch.object(vanish_sound.sys, "platform", "linux"):
            self.assertIsNone(vanish_sound.external_player(path))

    def test_ffplay_preferred_when_available(self):
        with patch.object(vanish_sound.shutil, "which", return_value="/opt/ffplay"):
            self.assertEqual(vanish_sound.external_player(Path("a.mp3"))[0], "/opt/ffplay")


class VirtualCameraHelpTests(unittest.TestCase):
    def test_macos_help_mentions_obs_system_extension(self):
        with patch.object(app.platform, "system", return_value="Darwin"):
            self.assertIn("OBS Studio 30", app.virtual_camera_help())
            self.assertIn(".command", app.virtual_camera_help())
        with patch.object(app.platform, "system", return_value="Windows"):
            self.assertIn("Unity Capture", app.virtual_camera_help())


if __name__ == "__main__":
    unittest.main()
