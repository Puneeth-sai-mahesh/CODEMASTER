"""Headless UI smoke test: drives every screen and (optionally) saves screenshots.

    xvfb-run -a -s "-screen 0 1280x1024x24" python tests/ui_smoke.py [screenshot_dir]
"""
import os
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
os.environ['HOME'] = tempfile.mkdtemp(prefix='cq_home_')
os.makedirs(os.path.join(os.environ['HOME'], '.config'), exist_ok=True)   # Kivy's user_data_dir uses mkdir, not makedirs
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_AUDIO'] = 'sdl2'

from kivy.config import Config  # noqa: E402

Config.set('graphics', 'width', '405')
Config.set('graphics', 'height', '780')
Config.set('graphics', 'resizable', '0')

from kivy.clock import Clock  # noqa: E402

import main  # noqa: E402

SHOTS = sys.argv[1] if len(sys.argv) > 1 else None
ERRORS = []


def shot(app, name):
    if SHOTS:
        os.makedirs(SHOTS, exist_ok=True)
        app.root.export_to_png(os.path.join(SHOTS, name + '.png'))


def check(cond, msg):
    if not cond:
        ERRORS.append(msg)
        print('FAIL:', msg)


def scenario(app):
    scr = app.screens
    yield 1.2
    shot(app, '01_home')

    app.goto('quest'); yield 0.6
    shot(app, '02_quest')

    # ---- a Python battle with a code question
    app.start_quiz('py', 3); yield 0.7
    q, s = scr['quiz'], scr['quiz'].s
    shot(app, '03_quiz_code')
    q.use_hint(); yield 0.2
    shot(app, '04_quiz_hint')
    q.choose(s.current.answer); yield 0.3
    shot(app, '05_quiz_right')
    q.next(); yield 0.3
    q.choose((s.current.answer + 1) % 4); yield 0.5
    shot(app, '06_quiz_wrong')
    q.next(); yield 0.2
    q.time_left = 0.02; yield 0.3
    check(s.answered and s.mistakes == 2, 'timer expiry should count as a mistake')
    q.next(); yield 0.2
    while True:
        q.choose(s.current.answer)
        if s.over:
            break
        q.next()
    q.next(); yield 2.0
    shot(app, '07_result_win')
    check(app.profile.stars_for('py', 3) in (0, 1, 2, 3), 'stars recorded')

    # ---- a C battle that we lose
    app.start_quiz('c', 1); yield 0.6
    s = scr['quiz'].s
    while not s.over:
        scr['quiz'].choose((s.current.answer + 1) % 4)
        if s.over:
            break
        scr['quiz'].next()
    scr['quiz'].next(); yield 1.0
    shot(app, '08_result_lose')

    # ---- daily
    app.start_daily(); yield 0.6
    shot(app, '09_daily')
    s = scr['quiz'].s
    while True:
        scr['quiz'].choose(s.current.answer)
        if s.over:
            break
        scr['quiz'].next()
    scr['quiz'].next(); yield 1.0
    check(not app.profile.daily_available(), 'daily should be marked done')

    # ---- learn
    app.goto('learn'); yield 0.5
    shot(app, '10_learn')
    app.open_lesson('c', 1); yield 0.5
    shot(app, '11_lesson')
    app.open_lesson('ds', 2); yield 0.4

    # ---- mini-games
    app.goto('minis'); yield 0.5
    shot(app, '12_minis')
    app.start_mini('stack', 2); yield 0.5
    st = scr['stack']
    shot(app, '13_stack_start')
    st.do_pop(); st.do_push(); st.do_push(); yield 0.2
    shot(app, '14_stack_mid')
    st.do_reset(); yield 0.2
    while not st.g.solved:
        mv = st.g.next_move()
        st.do_push() if mv == 'push' else st.do_pop()
    yield 1.6
    shot(app, '15_stack_result')

    app.start_mini('binary', 3); yield 0.5
    shot(app, '16_binary_start')
    b = scr['binary']
    first = b.g.best_guess()
    b.tap(first)
    yield 0.2
    shot(app, '17_binary_mid')
    while not b.g.over:
        b.tap(b.g.best_guess())
    yield 1.6
    shot(app, '18_binary_result')

    app.start_mini('bug', 2); yield 0.5
    bg = scr['bug']
    shot(app, '19_bug_start')
    bg.tap((bg.g.current['bug'] + 1) % len(bg.g.current['lines'])); yield 0.4
    shot(app, '20_bug_wrong')
    while True:
        if bg.g.over:
            break
        if not bg.g.answered:
            bg.tap(bg.g.current['bug'])
        if bg.g.over:
            break
        bg.next()
    bg.next(); yield 1.6
    shot(app, '21_bug_result')

    app.goto('trophies'); yield 0.5
    shot(app, '22_trophies')
    app.goto('settings'); yield 0.5
    shot(app, '23_settings')
    se = scr['settings']
    se.toggle('sound'); se.toggle('sound')
    check(app.profile.data['settings']['sound'] is True, 'toggle twice returns to ON')

    app.goto('home', 'right'); yield 0.6
    shot(app, '24_home_after')
    check(app.profile.xp > 0 and app.profile.data['badges'], 'xp and badges should have been earned')
    check(os.path.exists(app.profile.path), 'save file written')


def main_run():
    app = main.CodeQuestApp()
    gen = None

    def step(dt):
        nonlocal gen
        try:
            delay = next(gen)
        except StopIteration:
            app.stop()
            return
        except Exception:
            traceback.print_exc()
            ERRORS.append('exception in scenario')
            app.stop()
            return
        Clock.schedule_once(step, delay)

    def begin(dt):
        nonlocal gen
        gen = scenario(app)
        step(0)

    Clock.schedule_once(begin, 0.8)
    app.run()
    print('RESULT:', 'PASS' if not ERRORS else 'FAIL %s' % ERRORS)
    sys.exit(1 if ERRORS else 0)


if __name__ == '__main__':
    main_run()
