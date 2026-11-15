# Code Quest

A mobile game that teaches **Data Structures, Python and C**.

- 3 tracks x 3 difficulties (Easy / Medium / Hard), 72 questions. Every "What does this print?" answer was verified by running the real code.
- Battle a Bug Monster: timer, lives, combo multiplier, hints, XP, levels, ranks.
- 3 mini-games: **Stack Stacker** (LIFO), **Binary Hunt** (binary search), **Bug Hunter** (find the broken line).
- Learn section (14 short lessons), Daily Challenge, 12 badges, coins and hint shop, day streak.
- Haptics (vibration), synthesized sound effects, progress saved on the phone.

---

## Get the APK (about 20 minutes the first time, no installs on your PC)

The APK is built for free by GitHub. You only need a browser.

1. Make a free account at https://github.com
2. Click **+** (top right) > **New repository**. Name: `codequest`. Keep it **Public**. Click **Create repository**.
3. Click **uploading an existing file**. Unzip this project, then drag **everything inside the `codequest` folder** into the page, including the `.github` folder, `assets`, `tests` and all `.py` files. Click **Commit changes**.
   - Mac: press `Cmd + Shift + .` in Finder to see the hidden `.github` folder.
   - If `.github` will not upload: click **Add file > Create new file**, type `.github/workflows/build-apk.yml` as the name, paste the contents of `build-apk.yml` from this project, and commit.
4. Open the **Actions** tab. If it asks, click **I understand my workflows, enable them**. A run called **Build Android APK** starts by itself. (Or open it and press **Run workflow**.)
5. Wait for the green tick. The first build takes 15-30 minutes because it downloads the Android tools. Later builds take about 5 minutes.
6. Click the finished run, scroll to **Artifacts**, download **CodeQuest-apk**, and unzip it. Inside is the `.apk` file (its name starts with `codequest-1.0.0`).

### Install on your phone

1. Copy the `.apk` to your phone (WhatsApp to yourself, Google Drive, USB cable, anything).
2. Open it. If Android blocks it, tap **Settings** and allow **Install unknown apps** for the app you opened it from.
3. Tap **Install**, then **Open**.

### If the build fails (red cross)

Open the failed run, click the red step, copy the last ~40 lines of the log and send them to me. Most failures are a one-line fix in `buildozer.spec`.

---

## Try it on a computer first

```
pip install kivy
python main.py
```

Run the tests: `pip install pytest` then `python -m pytest -q`

---

## Files

| File | What it does |
|---|---|
| `main.py` | All screens and the app |
| `engine.py` | Quiz rules, XP, levels, badges, save file |
| `minigames.py` | Logic of the three mini-games |
| `questions.py`, `lessons.py` | All content - add your own questions here |
| `widgets.py`, `theme.py` | Buttons, monster, stars, colors |
| `haptics.py`, `sfx.py` | Vibration and sound |
| `buildozer.spec` | Android build settings (name, icon, permissions) |

### Add a question

In `questions.py`, copy any `Q(...)` line. The **first** option is the correct one (the game shuffles them). Difficulty: 1 easy, 2 medium, 3 hard. Keep code lines under 38 characters so they fit a phone screen. `python -m pytest` runs your Python/C snippets and tells you if the marked answer is wrong.
