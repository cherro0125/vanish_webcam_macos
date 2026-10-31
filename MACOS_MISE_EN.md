# VanishCam on macOS with mise: step-by-step guide

🇵🇱 [Wersja polska](MACOS_MISE_PL.md)

In this guide, [mise](https://mise.jdx.dev/) manages Python, and the app runs in its own virtual environment (`.venv-local`). You don't need to set up `mise activate` in your shell or install Python from python.org or Homebrew.

It works on Apple Silicon (M1–M4) and Intel Macs.

---

## Contents

1. [Install mise](#1-install-mise)
2. [Get the code](#2-get-the-code)
3. [Install Python with mise](#3-install-python-with-mise)
4. [Set up the environment and dependencies](#4-set-up-the-environment-and-dependencies)
5. [First run and camera access](#5-first-run-and-camera-access)
6. [Set up the OBS virtual camera (optional)](#6-set-up-the-obs-virtual-camera-optional)
7. [Background modes](#7-background-modes)
8. [Ready-made commands](#8-ready-made-commands)
9. [All options](#9-all-options)
10. [Keys](#10-keys)
11. [Zoom, Meet, Teams](#11-zoom-meet-teams)
12. [Update](#12-update)
13. [Troubleshooting](#13-troubleshooting)
14. [Uninstall](#14-uninstall)

---

## 1. Install mise

```bash
brew install mise
```

Without Homebrew, use the official installer: `curl https://mise.run | sh`.

Check the installation:

```bash
mise --version
```

## 2. Get the code

```bash
git clone https://github.com/cherro0125/vanish_webcam_macos.git
cd vanish_webcam_macos
```

## 3. Install Python with mise

```bash
mise install python@3.12
mise exec python@3.12 -- python --version   # should print Python 3.12.x
```

Python 3.12 works on every Mac. MediaPipe supports Python 3.9–3.13 on Apple Silicon and 3.9–3.12 on Intel. Python 3.14 doesn't work yet because `pygame` has no prebuilt package for it.

## 4. Set up the environment and dependencies

Run every command from the `vanish_webcam_macos` folder:

```bash
mise exec python@3.12 -- python -m venv .venv-local
.venv-local/bin/python -m pip install --upgrade pip
.venv-local/bin/python -m pip install -r requirements.txt
```

- The installation takes a few minutes and needs internet. You only do it once.
- The venv remembers its Python, so **you don't need mise to run the app**.
- `requirements.txt` picks the right package versions: MediaPipe 1.2.0 on Apple Silicon, and MediaPipe 0.10.21 with NumPy 1.x on Intel.

## 5. First run and camera access

```bash
.venv-local/bin/python vanish_cam.py
```

1. On the first run, the app downloads the MediaPipe models into `models/`.
2. macOS asks for camera access for **Terminal**. Click **Allow**.
3. If "Don't Allow" was clicked, open **System Settings → Privacy & Security → Camera**. Enable Terminal (or iTerm, VS Code, whichever app you run from), quit it completely (⌘Q), and open it again.
4. A menu appears. Pick `1` (Normal) or `2` (Naruto).
5. **Step out of the frame for 4 seconds.** The terminal tells you when to come back.
6. Vanish with a gesture: a **V sign** (index and middle finger) in Normal mode, or **palms together** in Naruto mode. You can also press `V`.

> The terminal messages are in Italian: *"Esci dall'inquadratura"* means "step out of the frame", and *"Puoi rientrare"* means "you can come back".

**Shortcut (optional).** Add an alias with the full project path to `~/.zshrc`:

```bash
alias vanish='~/vanish_webcam_macos/.venv-local/bin/python ~/vanish_webcam_macos/vanish_cam.py'
```

Then you can type, for example, `vanish --live-background` from any folder.

## 6. Set up the OBS virtual camera (optional)

You need this step only if the effect should appear as a camera in Zoom, Meet, or Teams. You do it once:

1. Install [OBS Studio](https://obsproject.com/) 30 or later, for example with `brew install --cask obs`.
2. Open OBS and click **Start Virtual Camera**.
3. When macOS asks, allow the OBS system extension in System Settings.
4. Click **Stop Virtual Camera** and quit OBS.

**OBS doesn't need to be running after this.** VanishCam sends its output to "OBS Virtual Camera" on its own, and the terminal then prints `Uscita virtuale attiva`. Without this setup, the app still runs with just the preview window.

## 7. Background modes

| Mode | Option | How it works |
|---|---|---|
| Classic | *(none)* | Takes one background photo. After you vanish, the picture stays frozen |
| **Live background** (recommended) | `--live-background` | The background keeps learning. After you vanish, the room stays live |
| No stepping out | `--fill-unseen` | Starts at once. Areas the camera has never seen are painted in |

### Live background: `--live-background`

```bash
.venv-local/bin/python vanish_cam.py --live-background
```

1. Place the camera so it **doesn't move** (on a monitor or a tripod).
2. Step out of the frame for 4 seconds to capture the background.
3. Come back and vanish with the gesture.
4. After you vanish, you can walk around the frame and stay invisible. People in the background, light changes, and moved objects are visible.
5. When the light changes or something is moved, the background updates itself in under a second. You don't need to press SPACE.
6. Press `R` to reappear.

### No stepping out: `--fill-unseen`

```bash
.venv-local/bin/python vanish_cam.py --fill-unseen
```

1. The app starts at once, without capturing a background.
2. Move a little to the left and right so the camera sees the room behind you. Every revealed spot is learned immediately.
3. Vanish. Spots the camera has never seen are painted in from their surroundings. This looks fine on a plain wall and blurry on a bookshelf or posters.
4. Press **SPACE** at any time and step out of the frame for 4 seconds to capture a clean background.

`--fill-unseen` turns on `--live-background` by itself.

### Limitations of both modes

- The camera must not move.
- The camera can't see what changes directly behind you, so that spot keeps the last view.
- Your shadow and your reflection in glass stay in the frame.
- Both modes use more CPU than the classic mode. If the picture stutters, lower the resolution.

## 8. Ready-made commands

```bash
# Normal with live background, no menu
.venv-local/bin/python vanish_cam.py --mode normal --live-background

# Naruto with live background
.venv-local/bin/python vanish_cam.py --mode naruto --live-background

# Naruto without stepping out of the frame
.venv-local/bin/python vanish_cam.py --mode naruto --fill-unseen

# For video calls: stop with an error if the OBS virtual camera doesn't work
.venv-local/bin/python vanish_cam.py --virtual-camera --live-background

# Without OBS: preview window only, to share in a call
.venv-local/bin/python vanish_cam.py --no-virtual-camera --live-background

# Slower Mac, or the picture stutters
.venv-local/bin/python vanish_cam.py --live-background --width 640 --height 360

# Another camera (e.g. iPhone through Continuity Camera), fullscreen
.venv-local/bin/python vanish_cam.py --live-background --camera 1 --fullscreen

# The gesture doesn't work: print recognition info in the terminal
.venv-local/bin/python vanish_cam.py --gesture-debug
```

## 9. All options

| Option | What it does |
|---|---|
| `--mode normal` / `--mode naruto` | Skips the menu and starts the chosen mode |
| `--live-background` | The background keeps learning, and the room stays live after you vanish |
| `--fill-unseen` | Paints in never-seen areas and skips background capture. Turns on `--live-background` |
| `--camera N` | Camera number (default `0`) |
| `--width N` / `--height N` | Resolution (default 960×540) |
| `--fps N` | Maximum frames per second for the virtual camera (default 30) |
| `--fullscreen` | Starts in fullscreen |
| `--no-mirror` | Turns off mirroring |
| `--virtual-camera` | Requires the virtual camera. Without it, the app stops with an error |
| `--no-virtual-camera` | Turns off the virtual camera and keeps only the preview window |
| `--gesture-debug` | Prints gesture recognition info in the terminal |

Full list: `.venv-local/bin/python vanish_cam.py --help`.

## 10. Keys

The keys work while the preview window is focused:

| Key | Action |
|---|---|
| `V` | vanish manually |
| `R` | reappear |
| `SPACE` | capture a new background (4 s out of the frame) |
| `F` | toggle fullscreen |
| `Q` / `ESC` | quit |

## 11. Zoom, Meet, Teams

- **With OBS (step 6):** pick **OBS Virtual Camera** in the call app's video settings. If it doesn't show up, restart the app or browser.
- **Without OBS:** run with `--no-virtual-camera` and share the **Webcam - Anteprima** window in the call. Others see it as a shared screen, not as a camera.

## 12. Update

```bash
cd vanish_webcam_macos
git pull
.venv-local/bin/python -m pip install -r requirements.txt
```

**Changing the Python version** (for example, to 3.13 on Apple Silicon):

```bash
rm -rf .venv-local
mise install python@3.13
mise exec python@3.13 -- python -m venv .venv-local
.venv-local/bin/python -m pip install -r requirements.txt
```

## 13. Troubleshooting

| Message or symptom | Fix |
|---|---|
| `Webcam 0 non disponibile` | Close other apps that use the camera, try `--camera 1`, and check the permission (step 5) |
| The app aborts with `Check failed: service_ Service is unavailable` | You have MediaPipe 1.0.1, which has a bug on Apple Silicon. Update the dependencies: `git pull`, then `.venv-local/bin/python -m pip install -r requirements.txt` (installs 1.2.0) |
| `not authorized to capture video` on the first run | Click **Allow** in the macOS dialog. The app waits up to 30 s. If no dialog appears, check the permission (step 5) |
| `Webcam virtuale non disponibile` | Repeat step 6. The OBS virtual camera must be **stopped** |
| `pip install` fails (no package for this version) | Your Python is outside the supported range. Recreate the venv with 3.12 (step 12) |
| `mise: command not found` | Open a new Terminal after installing. With the `curl` installer, add `~/.local/bin` to `PATH` |
| Outline or "hole" where the person was | The camera moved or the light changed. Press SPACE, use a tripod and steady light |
| The picture stutters | `--width 640 --height 360` |
| The gesture doesn't work | Use better front lighting, keep your whole hand in the frame, try `--gesture-debug`, or press `V` |
| No sound in Naruto mode | Check the volume. Without `pygame`, the app plays the sound with the built-in macOS `afplay` |

## 14. Uninstall

```bash
rm -rf vanish_webcam_macos      # code, venv, and downloaded models
mise uninstall python@3.12      # only if nothing else needs this Python
```

You can revoke camera access in **System Settings → Privacy & Security → Camera**.
