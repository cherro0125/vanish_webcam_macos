# VanishCam na macOS z mise: instrukcja krok po kroku

🇬🇧 [English version](MACOS_MISE_EN.md)

W tej instrukcji Pythonem zarządza [mise](https://mise.jdx.dev/), a aplikacja działa we własnym środowisku wirtualnym (`.venv-local`). Nie musisz konfigurować `mise activate` w shellu ani instalować Pythona z python.org czy Homebrew.

Działa na Macach z Apple Silicon (M1–M4) i z procesorem Intel.

---

## Spis treści

1. [Instalacja mise](#1-instalacja-mise)
2. [Pobranie kodu](#2-pobranie-kodu)
3. [Python przez mise](#3-python-przez-mise)
4. [Środowisko i zależności](#4-środowisko-i-zależności)
5. [Pierwsze uruchomienie i dostęp do kamery](#5-pierwsze-uruchomienie-i-dostęp-do-kamery)
6. [Wirtualna kamera przez OBS (opcjonalnie)](#6-wirtualna-kamera-przez-obs-opcjonalnie)
7. [Tryby tła](#7-tryby-tła)
8. [Gotowe komendy](#8-gotowe-komendy)
9. [Wszystkie opcje](#9-wszystkie-opcje)
10. [Klawisze](#10-klawisze)
11. [Zoom, Meet, Teams](#11-zoom-meet-teams)
12. [Aktualizacja](#12-aktualizacja)
13. [Rozwiązywanie problemów](#13-rozwiązywanie-problemów)
14. [Odinstalowanie](#14-odinstalowanie)

---

## 1. Instalacja mise

```bash
brew install mise
```

Bez Homebrew użyj oficjalnego instalatora: `curl https://mise.run | sh`.

Sprawdź instalację:

```bash
mise --version
```

## 2. Pobranie kodu

```bash
git clone https://github.com/cherro0125/vanish_webcam_macos.git
cd vanish_webcam_macos
```

> Opcje `--live-background` i `--fill-unseen` są w PR #2. Dopóki nie zostanie zmergowany, przełącz się na jego gałąź:
>
> ```bash
> git checkout live-background
> ```

## 3. Python przez mise

```bash
mise install python@3.12
mise exec python@3.12 -- python --version   # powinno pokazać Python 3.12.x
```

Python 3.12 działa na każdym Macu. MediaPipe obsługuje Pythona 3.9–3.13 na Apple Silicon i 3.9–3.12 na Intelu. Wersja 3.14 jeszcze nie działa, bo nie ma dla niej gotowej paczki `pygame`.

## 4. Środowisko i zależności

Wszystkie komendy wykonuj w folderze `vanish_webcam_macos`:

```bash
mise exec python@3.12 -- python -m venv .venv-local
.venv-local/bin/python -m pip install --upgrade pip
.venv-local/bin/python -m pip install -r requirements.txt
```

- Instalacja trwa kilka minut i wymaga internetu. To jednorazowy krok.
- Venv zapamiętuje swojego Pythona, więc **do uruchamiania aplikacji mise nie jest już potrzebny**.
- `requirements.txt` sam wybiera wersje paczek: na Apple Silicon instaluje MediaPipe 1.0.1, a na Intelu MediaPipe 0.10.21 z NumPy 1.x.

## 5. Pierwsze uruchomienie i dostęp do kamery

```bash
.venv-local/bin/python vanish_cam.py
```

1. Przy pierwszym uruchomieniu aplikacja pobiera modele MediaPipe do folderu `models/`.
2. macOS zapyta o dostęp do kamery dla **Terminala**. Kliknij **Pozwól**.
3. Jeśli kliknięto „Nie pozwalaj”, otwórz **Ustawienia systemowe → Prywatność i ochrona → Kamera**. Włącz Terminal (albo iTerm, VS Code, czyli aplikację, z której uruchamiasz), zamknij ją całkowicie (⌘Q) i otwórz ponownie.
4. Pojawi się menu. Wybierz `1` (Normal) albo `2` (Naruto).
5. **Wyjdź z kadru na 4 sekundy.** Terminal powie, kiedy wrócić.
6. Zniknij gestem: **znak V** (palec wskazujący i środkowy) w trybie Normal albo **złączone dłonie** w trybie Naruto. Możesz też nacisnąć `V`.

> Komunikaty w terminalu są po włosku: *„Esci dall'inquadratura”* znaczy „wyjdź z kadru”, a *„Puoi rientrare”* znaczy „możesz wrócić”.

**Skrót (opcjonalnie).** Dopisz do `~/.zshrc` alias z pełną ścieżką do projektu:

```bash
alias vanish='~/vanish_webcam_macos/.venv-local/bin/python ~/vanish_webcam_macos/vanish_cam.py'
```

Potem wystarczy wpisać np. `vanish --live-background`, z dowolnego folderu.

## 6. Wirtualna kamera przez OBS (opcjonalnie)

Ten krok jest potrzebny tylko wtedy, gdy efekt ma być widoczny jako kamera w Zoomie, Meet albo Teams. Wykonujesz go raz:

1. Zainstaluj [OBS Studio](https://obsproject.com/) w wersji 30 lub nowszej, np. `brew install --cask obs`.
2. Otwórz OBS i kliknij **Start Virtual Camera** (Uruchom wirtualną kamerę).
3. Gdy macOS zapyta, zezwól na rozszerzenie systemowe OBS w Ustawieniach systemowych.
4. Kliknij **Stop Virtual Camera** i zamknij OBS.

**OBS nie musi być potem uruchomiony.** VanishCam sam wysyła obraz do „OBS Virtual Camera”, a terminal wypisuje wtedy `Uscita virtuale attiva`. Bez tej konfiguracji aplikacja działa dalej z samym oknem podglądu.

## 7. Tryby tła

| Tryb | Opcja | Jak działa |
|---|---|---|
| Klasyczny | *(brak)* | Zdjęcie tła robione raz. Po zniknięciu obraz stoi w miejscu |
| **Żywe tło** (polecany) | `--live-background` | Tło uczy się na bieżąco. Po zniknięciu pokój jest na żywo |
| Bez wychodzenia z kadru | `--fill-unseen` | Start od razu. Niewidziane miejsca są domalowywane |

### Żywe tło: `--live-background`

```bash
.venv-local/bin/python vanish_cam.py --live-background
```

1. Ustaw kamerę tak, żeby **się nie ruszała** (monitor albo statyw).
2. Wyjdź z kadru na 4 sekundy, żeby nagrać tło.
3. Wróć i zniknij gestem.
4. Po zniknięciu możesz chodzić po kadrze i nadal być niewidoczny. Ludzie w tle, zmiany światła i przesunięte przedmioty są widoczne.
5. Gdy zmieni się światło albo coś zostanie przesunięte, tło aktualizuje się samo w niecałą sekundę. Nie trzeba naciskać SPACJI.
6. `R` przywraca Cię na ekran.

### Bez wychodzenia z kadru: `--fill-unseen`

```bash
.venv-local/bin/python vanish_cam.py --fill-unseen
```

1. Aplikacja startuje od razu, bez nagrywania tła.
2. Przesuń się trochę w lewo i w prawo, żeby kamera zobaczyła pokój za Tobą. Każde odsłonięte miejsce jest od razu zapamiętywane.
3. Zniknij. Miejsca, których kamera nigdy nie widziała, są domalowywane na podstawie otoczenia. Na gładkiej ścianie wygląda to dobrze, a na regale albo plakatach będzie rozmyte.
4. W dowolnej chwili możesz nacisnąć **SPACJĘ** i wyjść z kadru na 4 sekundy, żeby nagrać czyste tło.

`--fill-unseen` sam włącza `--live-background`.

### Ograniczenia obu trybów

- Kamera nie może się ruszać.
- Kamera nie widzi tego, co zmienia się dokładnie za Tobą, więc w tym miejscu zostaje ostatni widok.
- Cień i odbicie w szybie zostają w kadrze.
- Oba tryby obciążają procesor bardziej niż tryb klasyczny. Jeśli obraz się tnie, zmniejsz rozdzielczość.

## 8. Gotowe komendy

```bash
# Normal z żywym tłem, bez menu
.venv-local/bin/python vanish_cam.py --mode normal --live-background

# Naruto z żywym tłem
.venv-local/bin/python vanish_cam.py --mode naruto --live-background

# Naruto bez wychodzenia z kadru
.venv-local/bin/python vanish_cam.py --mode naruto --fill-unseen

# Do rozmów wideo: przerwij, jeśli wirtualna kamera OBS nie działa
.venv-local/bin/python vanish_cam.py --virtual-camera --live-background

# Bez OBS: samo okno podglądu do udostępnienia w rozmowie
.venv-local/bin/python vanish_cam.py --no-virtual-camera --live-background

# Słabszy Mac albo obraz się tnie
.venv-local/bin/python vanish_cam.py --live-background --width 640 --height 360

# Inna kamera (np. iPhone przez Continuity Camera), pełny ekran
.venv-local/bin/python vanish_cam.py --live-background --camera 1 --fullscreen

# Gest nie działa: informacje o rozpoznawaniu w terminalu
.venv-local/bin/python vanish_cam.py --gesture-debug
```

## 9. Wszystkie opcje

| Opcja | Co robi |
|---|---|
| `--mode normal` / `--mode naruto` | Pomija menu i od razu uruchamia wybrany tryb |
| `--live-background` | Tło uczy się na bieżąco, a po zniknięciu obraz jest na żywo |
| `--fill-unseen` | Domalowuje niewidziane miejsca i pomija nagrywanie tła. Sama włącza `--live-background` |
| `--camera N` | Numer kamery (domyślnie `0`) |
| `--width N` / `--height N` | Rozdzielczość (domyślnie 960×540) |
| `--fps N` | Maksymalna liczba klatek na sekundę dla wirtualnej kamery (domyślnie 30) |
| `--fullscreen` | Start na pełnym ekranie |
| `--no-mirror` | Wyłącza lustrzane odbicie obrazu |
| `--virtual-camera` | Wymaga wirtualnej kamery. Bez niej aplikacja zakończy się błędem |
| `--no-virtual-camera` | Wyłącza wirtualną kamerę i zostawia samo okno podglądu |
| `--gesture-debug` | Wypisuje w terminalu informacje o rozpoznawaniu gestów |

Pełna lista: `.venv-local/bin/python vanish_cam.py --help`.

## 10. Klawisze

Klawisze działają, gdy okno podglądu jest aktywne:

| Klawisz | Akcja |
|---|---|
| `V` | zniknij ręcznie |
| `R` | pojaw się z powrotem |
| `SPACJA` | nagraj nowe tło (4 s poza kadrem) |
| `F` | pełny ekran |
| `Q` / `ESC` | wyjście |

## 11. Zoom, Meet, Teams

- **Z OBS (punkt 6):** w ustawieniach wideo aplikacji do rozmów wybierz kamerę **OBS Virtual Camera**. Jeśli jej nie widać, zrestartuj tę aplikację albo przeglądarkę.
- **Bez OBS:** uruchom z `--no-virtual-camera` i w rozmowie udostępnij okno **Webcam - Anteprima**. Rozmówcy zobaczą je jako udostępniony ekran, a nie kamerę.

## 12. Aktualizacja

```bash
cd vanish_webcam_macos
git pull
.venv-local/bin/python -m pip install -r requirements.txt
```

**Zmiana wersji Pythona** (np. na 3.13 na Apple Silicon):

```bash
rm -rf .venv-local
mise install python@3.13
mise exec python@3.13 -- python -m venv .venv-local
.venv-local/bin/python -m pip install -r requirements.txt
```

## 13. Rozwiązywanie problemów

| Komunikat lub objaw | Rozwiązanie |
|---|---|
| `Webcam 0 non disponibile` | Zamknij inne aplikacje używające kamery, spróbuj `--camera 1`, sprawdź uprawnienia (punkt 5) |
| `Webcam virtuale non disponibile` | Powtórz punkt 6. Wirtualna kamera w OBS musi być **zatrzymana** |
| Błąd przy `pip install` (brak paczki dla danej wersji) | Masz Pythona spoza obsługiwanego zakresu. Odtwórz venv z 3.12 (punkt 12) |
| `mise: command not found` | Otwórz nowy Terminal po instalacji. Przy instalatorze `curl` dodaj `~/.local/bin` do `PATH` |
| Obrys sylwetki albo „dziura” w miejscu osoby | Kamera się poruszyła albo zmieniło się światło. Naciśnij SPACJĘ, użyj statywu i stałego światła |
| Obraz się tnie | `--width 640 --height 360` |
| Gest nie działa | Lepsze światło z przodu, cała dłoń w kadrze, opcja `--gesture-debug` albo klawisz `V` |
| Brak dźwięku w trybie Naruto | Sprawdź głośność. Bez `pygame` aplikacja odtwarza dźwięk wbudowanym w macOS `afplay` |

## 14. Odinstalowanie

```bash
rm -rf vanish_webcam_macos      # kod, venv i pobrane modele
mise uninstall python@3.12      # tylko jeśli ten Python nie jest potrzebny do czegoś innego
```

Dostęp do kamery możesz cofnąć w **Ustawienia systemowe → Prywatność i ochrona → Kamera**.
