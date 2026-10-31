#!/bin/bash
# macOS: double-click in Finder or run ./AVVIA_LOCALE.command in Terminal.
# Same as AVVIA_LOCALE.bat: creates the Python environment, installs the
# dependencies on the first run and starts vanish_cam.py with the given arguments.
cd "$(dirname "$0")" || exit 1

VENV_DIR=".venv-local"
VENV_PY="$VENV_DIR/bin/python"

fail() {
  echo
  echo "Could not start Vanish Lab. $1"
  echo "See the macOS section of the README for common fixes."
  read -r -p "Press ENTER to close..." _
  exit 1
}

# MediaPipe publishes wheels only for some Python versions:
# Apple Silicon 3.9-3.13 (pygame does not support 3.14 yet), Intel 3.9-3.12.
if [ "$(uname -m)" = "arm64" ]; then
  MAX_MINOR=13
else
  MAX_MINOR=12
fi

python_ok() {
  "$1" -c "import sys; sys.exit(0 if (3, 9) <= sys.version_info[:2] <= (3, $MAX_MINOR) else 1)" >/dev/null 2>&1
}

if [ ! -x "$VENV_PY" ] || ! python_ok "$VENV_PY"; then
  PYTHON=""
  for candidate in python3.13 python3.12 python3.11 python3.10 python3.9 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && python_ok "$candidate"; then
      PYTHON="$candidate"
      break
    fi
  done
  if [ -z "$PYTHON" ]; then
    fail "Python 3.9-3.$MAX_MINOR is required: install it from https://www.python.org/downloads/macos/ or with 'brew install python@3.12'."
  fi
  echo "[Vanish Lab] Creating the local Python environment with $("$PYTHON" --version)..."
  rm -rf "$VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR" || fail "Could not create the Python environment."
fi

if ! "$VENV_PY" -c "import cv2, mediapipe, numpy, pyvirtualcam" >/dev/null 2>&1; then
  echo "[Vanish Lab] Installing the required components. Internet is needed only this time..."
  "$VENV_PY" -m pip install --upgrade pip || fail "Could not upgrade pip."
  "$VENV_PY" -m pip install -r requirements.txt || fail "Could not install the dependencies."
fi

echo "[Vanish Lab] Starting the webcam..."
echo "[Vanish Lab] On the first run macOS asks for camera permission: click Allow."
"$VENV_PY" vanish_cam.py "$@" || fail "Check the messages above."
