# VanishCam — webcam disappearance effects

Video is processed on your computer. It is neither recorded nor sent to a server. The preview window and virtual camera show only the video and effects, without overlaid menus, instructions, or text.

For step-by-step instructions in English and Italian, see the [user guide](USER_GUIDE_EN_IT.md).

## ☕ Buy me a coffee

If you like this project and want to support it, you can buy me a coffee through [PayPal](https://paypal.me/nicovic17) or [Revolut](https://revolut.me/nicoauriemma).

## Download for Windows

[Download VanishCam.exe]( https://nicoaauriemma.vercel.app/shop ) and double-click it to run the app. You do not need to install Python.

The published EXE may predate the Particles and Goku modes. To use them now, run the local scripts or rebuild the EXE from these sources.

## macOS

The app runs on macOS (Apple Silicon and Intel) from the Python sources. There is no prebuilt app.

If you manage Python with [mise](https://mise.jdx.dev/), follow the full step-by-step guide in [English](MACOS_MISE_EN.md) or [Polish](MACOS_MISE_PL.md). The steps below use the bundled launcher instead.

1. Install Python from [python.org](https://www.python.org/downloads/macos/) or with `brew install python@3.12`. Apple Silicon Macs need Python 3.9–3.13, and Intel Macs need 3.9–3.12, because MediaPipe publishes no newer builds for them.
2. Double-click `AVVIA_LOCALE.command` in Finder, or run `./AVVIA_LOCALE.command` in Terminal. On the first run it creates `.venv-local` and installs the dependencies. You need an internet connection for that.
3. macOS asks for camera access on the first run. Allow it. If you dismissed the prompt, open **System Settings → Privacy & Security → Camera**, enable the app you launch from (Terminal, iTerm, VS Code…), and restart that app.

If Finder says the script comes from an unidentified developer, right-click it and choose **Open**, or run `xattr -d com.apple.quarantine *.command` in the project folder. If double-clicking does nothing, run `chmod +x *.command`.

`AVVIA_VIRTUAL.command` and `AVVIA_OBS.command` work like their Windows `.bat` counterparts, and all of them accept the same options:

```bash
./AVVIA_LOCALE.command --mode naruto --camera 1 --width 1280 --height 720
```

**Virtual camera on macOS:** pyvirtualcam supports only the OBS virtual camera on macOS. Install [OBS Studio](https://obsproject.com/) 30 or later. Open it once, click **Start Virtual Camera**, and approve the system extension in System Settings when prompted. Then stop the virtual camera and quit OBS. VanishCam sends its output to **OBS Virtual Camera** while OBS is closed. Unity Capture is Windows-only.

Without OBS, use `AVVIA_OBS.command` (preview window only) and share the **Webcam - Anteprima** window in Zoom, Meet, or Teams.

If `pygame` is not installed, the Naruto sound falls back to `ffplay` or to the built-in macOS `afplay`.

## Getting started

1. Double-click `AVVIA_LOCALE.bat` (Windows) or `AVVIA_LOCALE.command` (macOS).
2. In the start menu, choose **Normal Vanish**, **Naruto Vanish**, **Particles**, or **Goku** with the mouse or the `1`, `2`, `3`, and `4` keys.
3. Step out of the camera frame for 4 seconds while the background is captured. The terminal tells you when you can step back in.

**Normal Vanish:** Raise your index and middle fingers in a V sign. The dissolve starts as soon as the gesture is recognized and lasts about 3.6 seconds.

**Particles:** Make the same V sign as in Normal Vanish. Your silhouette breaks into small colored fragments that drift sideways as if carried by the wind. The effect lasts about 2.1 seconds. It captures your silhouette once when the effect starts to keep the video smooth.

**Goku:** Hold your index and middle fingers straight and together against your forehead for 1 second. Animated vertical comic-style lines run across your silhouette just before you teleport away and linger briefly afterward. To reappear, lower your hand, then repeat the gesture for another 1 second. The return uses the reverse effect. If you break the pose, the countdown starts over. `assets/teleport.MP3` plays on both disappearance and reappearance. The terminal shows the countdown for each gesture. The `V` and `R` keys are disabled in this mode: the gesture is the only way to disappear and reappear. No text is overlaid on the video.

**Naruto Vanish:** Bring your palms together in front of the webcam, with your fingers side by side rather than interlaced. Keep both hands visible. As soon as the gesture is recognized, you vanish in a cloud of smoke and a wooden log appears, falls, and remains visible until you press `R`. No microphone is needed. Naruto mode uses `hand_landmarker.task` to track both hands. `assets/vanish.MP3` plays through your computer speakers when the disappearance starts, including when triggered with `V`. You can trigger it again after pressing `R`.

To start a mode without the menu:

```powershell
local_app\AVVIA_LOCALE.bat --mode naruto
local_app\AVVIA_LOCALE.bat --mode normal
local_app\AVVIA_LOCALE.bat --mode particles
local_app\AVVIA_LOCALE.bat --mode goku
```

## Virtual camera and OBS

If [OBS Studio](https://obsproject.com/) is installed, the app automatically tries to open **OBS Virtual Camera**. The terminal shows the device name. Use `AVVIA_VIRTUAL.bat` to require a virtual camera. Select **OBS Virtual Camera** in the app that will receive the video. OBS's virtual camera must be stopped while this app is producing its output.

To use the effect in an OBS scene, run `AVVIA_OBS.bat`, add a **Window Capture** source, select **Webcam - Anteprima**, and then start the virtual camera from OBS. Alternatively, use [Unity Capture](https://github.com/schellingb/UnityCapture) as a separate virtual video source:

```powershell
local_app\AVVIA_VIRTUAL.bat --virtual-backend unitycapture
```

OBS has only one virtual camera. Do not use it as both an OBS input and output at the same time. See the [pyvirtualcam documentation](https://github.com/letmaik/pyvirtualcam#supported-virtual-cameras).

## Controls

- `SPACE`: capture a new background.
- `R`: make the person reappear.
- `V`: manually start the selected mode's effect.
- `F`: toggle fullscreen.
- `Q` or `ESC`: quit and release the cameras.

The `V` and `R` keys are disabled in Goku mode.

You can change the camera, resolution, and maximum virtual-output FPS:

```powershell
local_app\AVVIA_LOCALE.bat --camera 1 --width 1280 --height 720 --fps 30
```

To troubleshoot gesture recognition without adding text to the video, pass `--gesture-debug`. Diagnostic information appears only in the terminal.

## Live background

By default, the app takes one photo of the empty room during calibration. That photo replaces you when you vanish, and the video stays frozen on it afterward. If the light changes, the camera moves, or an object is moved, the effect stops matching the room until you press `SPACE`.

`--live-background` keeps updating the background:

- Every part of the room you are not covering is refreshed continuously, so moved objects and light changes appear without recapturing.
- The area behind you keeps its last seen state. The app applies the room-wide light change it measures on the visible parts, so the patch behind you does not look brighter or darker than the rest of the room.
- After you vanish, the room stays live. People walking by and changing light are visible, and you stay cut out wherever you move.

`--fill-unseen` turns on `--live-background` and also paints in areas the camera has never seen, using their surroundings. You no longer have to leave the frame at startup: the app starts at once, and moving a little to the side reveals the real background. The painted areas are soft guesses. They look fine on a plain wall and blurry on detailed backgrounds. Press `SPACE` at any time to capture a clean background instead.

Windows:

```powershell
local_app\AVVIA_LOCALE.bat --live-background
local_app\AVVIA_LOCALE.bat --fill-unseen --mode naruto
```

macOS:

```bash
./AVVIA_LOCALE.command --live-background
./AVVIA_LOCALE.command --fill-unseen --mode naruto
```

Limitations:

- The camera must not move. A camera that moves breaks the background in either mode.
- Anything that changes directly behind you while you stand there is not visible to the camera, so the last seen state is shown.
- The app removes you but not your shadow or reflection.
- The silhouette is segmented continuously, even before you vanish, which costs more CPU than the default mode.

## Visual assets

The [wooden log](assets/substitution_log.png) is an original illustration generated with ImageGen using the supplied image as a visual reference. Smoke is drawn in real time by `naruto_effect.py` so it follows the person's position and scales with the video. We also considered a [CC0 smoke sprite sheet](https://opengameart.org/content/smoke-sprite-sheet), but the procedural animation adapts better to dynamic positioning without an additional asset. No anime frames or assets are included in the project.

Goku mode uses the [MediaPipe BlazeFace short-range model](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/tasks/web/vision/README.md) to estimate the forehead position and `hand_landmarker.task` to track the fingers. The teleport's visual trace is drawn in code, without anime frames.
