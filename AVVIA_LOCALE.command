#!/bin/bash
# macOS: doppio clic nel Finder oppure ./AVVIA_LOCALE.command dal Terminale.
# Equivalente di AVVIA_LOCALE.bat: crea l'ambiente Python, installa le
# dipendenze la prima volta e avvia vanish_cam.py con gli argomenti passati.
cd "$(dirname "$0")" || exit 1

VENV_DIR=".venv-local"
VENV_PY="$VENV_DIR/bin/python"

fail() {
  echo
  echo "Impossibile avviare Vanish Lab. $1"
  echo "Leggi la sezione macOS del README per le soluzioni comuni."
  read -r -p "Premi INVIO per chiudere..." _
  exit 1
}

# MediaPipe pubblica ruote solo per alcune versioni di Python:
# Apple Silicon 3.9-3.13 (pygame non supporta ancora 3.14), Intel 3.9-3.12.
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
    fail "Serve Python 3.9-3.$MAX_MINOR: installalo da https://www.python.org/downloads/macos/ oppure con 'brew install python@3.12'."
  fi
  echo "[Vanish Lab] Creo l'ambiente Python locale con $("$PYTHON" --version)..."
  rm -rf "$VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR" || fail "Creazione dell'ambiente Python non riuscita."
fi

if ! "$VENV_PY" -c "import cv2, mediapipe, numpy, pyvirtualcam" >/dev/null 2>&1; then
  echo "[Vanish Lab] Installo i componenti necessari. Serve internet solo questa volta..."
  "$VENV_PY" -m pip install --upgrade pip || fail "Aggiornamento di pip non riuscito."
  "$VENV_PY" -m pip install -r requirements.txt || fail "Installazione delle dipendenze non riuscita."
fi

echo "[Vanish Lab] Avvio la webcam..."
echo "[Vanish Lab] Al primo avvio macOS chiede il permesso per la fotocamera: consenti l'accesso."
"$VENV_PY" vanish_cam.py "$@" || fail "Controlla i messaggi qui sopra."
