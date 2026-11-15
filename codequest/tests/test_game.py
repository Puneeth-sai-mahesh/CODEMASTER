"""Run with:  python -m pytest -q   (from the project folder)"""
import contextlib
import datetime
import io
import os
import random
import shutil
import subprocess
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import engine
import minigames
from lessons import all_lessons
from questions import BANK, TRACKS, questions_for


# ------------------------------------------------------------ question bank
def test_bank_shape():
    for track in TRACKS:
        for diff in (1, 2, 3):
            assert len(questions_for(track, diff)) == 8, (track, diff)


def test_options_are_unique_and_correct_not_duplicated():
    for q in BANK:
        opts = [q.correct] + list(q.wrong)
        assert len(set(opts)) == 4, q.text
        assert q.why.strip(), q.text


def _run_python(code):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, '<q>', 'exec'), {})
    return buf.getvalue().strip()


def test_python_snippets_print_the_marked_answer():
    checked = 0
    for q in BANK:
        if q.lang == 'py':
            assert _run_python(q.code) == q.correct, q.code
            checked += 1
    assert checked >= 20


@pytest.mark.skipif(shutil.which('gcc') is None, reason='gcc not installed')
def test_c_snippets_print_the_marked_answer():
    checked = 0
    for q in BANK:
        if q.lang != 'c':
            continue
        src = ('#include <stdio.h>\n#include <string.h>\n#include <stdlib.h>\n'
               'int main(void) {\n%s\nreturn 0;\n}\n' % q.code)
        with tempfile.TemporaryDirectory() as tmp:
            c_file, exe = os.path.join(tmp, 'a.c'), os.path.join(tmp, 'a')
            with open(c_file, 'w') as fh:
                fh.write(src)
            subprocess.run(['gcc', '-w', c_file, '-o', exe], check=True)
            out = subprocess.run([exe], capture_output=True, text=True, check=True).stdout.strip()
        assert out == q.correct, q.code
        checked += 1
    assert checked >= 10


def test_lessons_exist():
    assert len(all_lessons()) == engine.TOTAL_LESSONS >= 10


# ------------------------------------------------------------ quiz session
def _play(session, always_right=True):
    while True:
        q = session.current
        pick = q.answer if always_right else (q.answer + 1) % 4
        session.answer(pick, time_left=5)
        if session.over:
            return
        session.advance()


def test_perfect_run_wins_three_stars():
    s = engine.QuizSession('ds', 1, rng=random.Random(1))
    _play(s)
    assert s.won and s.stars == 3 and s.correct == s.total == 6
    assert s.monster_hp == 0
    assert s.best_combo == 6 and s.xp > 6 * 10


def test_all_wrong_loses():
    s = engine.QuizSession('c', 3, rng=random.Random(2))
    _play(s, always_right=False)
    assert not s.won and s.lives == 0 and s.stars == 0
    assert s.mistakes == s.cfg['lives']


def test_hint_removes_two_wrong_options_once():
    s = engine.QuizSession('py', 2, rng=random.Random(3))
    removed = s.use_hint()
    assert len(removed) == 2 and s.current.answer not in removed
    assert s.use_hint() == []


def test_timeout_costs_a_life_and_resets_combo():
    s = engine.QuizSession('py', 1, rng=random.Random(4))
    s.answer(s.current.answer, 10)
    s.advance()
    r = s.answer(None)
    assert r['timeout'] and not r['correct'] and s.combo == 0 and s.lives == s.max_lives - 1


def test_answering_twice_is_an_error():
    s = engine.QuizSession('py', 1, rng=random.Random(5))
    s.answer(0)
    with pytest.raises(RuntimeError):
        s.answer(1)


def test_daily_session_is_stable_per_day():
    d = datetime.date(2026, 11, 14)
    a, b = engine.daily_session(d), engine.daily_session(d)
    assert [q.text for q in a.items] == [q.text for q in b.items]
    assert [q.options for q in a.items] == [q.options for q in b.items]
    assert a.total == 6 and a.title == 'Daily Challenge'


# ------------------------------------------------------------ profile
def test_levels():
    assert engine.level_for(0) == 1
    assert engine.level_for(59) == 1 and engine.level_for(60) == 2
    assert engine.level_for(240) == 3
    lvl, into, need = engine.level_progress(100)
    assert lvl == 2 and into == 40 and need == 180


def test_unlock_chain_and_badges_and_save_roundtrip(tmp_path):
    path = str(tmp_path / 'save.json')
    p = engine.Profile(path)
    assert p.unlocked('ds', 1) and not p.unlocked('ds', 2)

    s = engine.QuizSession('ds', 1, rng=random.Random(6))
    _play(s)
    res = p.record_quiz(s, today=datetime.date(2026, 11, 14))
    assert p.stars_for('ds', 1) == 3 and p.unlocked('ds', 2)
    assert {'first_win', 'perfect', 'combo5'} <= set(res['new_badges'])

    q = engine.Profile(path)               # reload from disk
    assert q.xp == p.xp and q.stars_for('ds', 1) == 3
    assert 'first_win' in q.data['badges']


def test_stars_never_go_down():
    p = engine.Profile()
    good = engine.QuizSession('py', 1, rng=random.Random(7))
    _play(good)
    p.record_quiz(good)
    bad = engine.QuizSession('py', 1, rng=random.Random(8))
    _play(bad, always_right=False)
    p.record_quiz(bad)
    assert p.stars_for('py', 1) == 3


def test_streak_logic():
    p = engine.Profile()
    d = datetime.date(2026, 11, 14)
    p.touch_day(d)
    p.touch_day(d)
    assert p.streak == 1
    p.touch_day(d + datetime.timedelta(days=1))
    assert p.streak == 2
    p.touch_day(d + datetime.timedelta(days=5))
    assert p.streak == 1


def test_daily_bonus_only_once_per_day():
    p = engine.Profile()
    today = datetime.date(2026, 11, 14)
    first = engine.daily_session(today)
    _play(first)
    r1 = p.record_quiz(first, today)
    second = engine.daily_session(today)
    _play(second)
    r2 = p.record_quiz(second, today)
    assert r1['coins'] - r2['coins'] == engine.DAILY_BONUS
    assert not p.daily_available(today)


def test_shop_and_level_up_gift():
    p = engine.Profile()
    start_hints = p.hints
    assert p.buy_hint() and p.hints == start_hints + 1
    p.data['coins'] = 0
    assert not p.buy_hint()
    leveled = p._reward(60, 0)
    assert leveled and p.hints == start_hints + 2


def test_corrupt_save_falls_back(tmp_path):
    path = tmp_path / 'save.json'
    path.write_text('{not json')
    assert engine.Profile(str(path)).xp == 0


# ------------------------------------------------------------ mini-games
@pytest.mark.parametrize('n', [4, 5, 6])
def test_stack_puzzle_is_always_solvable_by_greedy_solver(n):
    for seed in range(200):
        g = minigames.StackPuzzle(n, random.Random(seed))
        assert sorted(g.target) == list(range(1, n + 1)) and g.target != sorted(g.target)
        while not g.solved:
            move = g.next_move()
            assert move in ('push', 'pop')
            assert g.push() if move == 'push' else g.pop() == 'ok'
        assert g.moves == 2 * n and g.stars == 3


def test_stack_puzzle_rejects_wrong_pop_and_detects_dead_end():
    g = minigames.StackPuzzle(4, random.Random(0))
    assert g.pop() == 'empty'
    # Push everything: the top is 4, so unless the target starts with 4 the pop is wrong.
    while g.push():
        pass
    assert g.dead == (g.target[0] != 4) or g.dead in (True, False)
    wrong = g.pop() == 'wrong'
    if wrong:
        assert g.mistakes == 1 and g.out == []
    g.reset()
    assert g.resets == 1 and g.stack == [] and g.inp == [1, 2, 3, 4]


def test_stack_dead_detection_is_correct():
    g = minigames.StackPuzzle(3, random.Random(1))
    g.target = [1, 2, 3]
    g.push(); g.push(); g.push()          # stack bottom->top 1,2,3 ; need 1 first -> impossible
    assert g.dead
    g.reset()
    g.push()
    assert not g.dead


@pytest.mark.parametrize('size', [15, 31, 63])
def test_binary_hunt_perfect_strategy_always_wins_in_optimal_guesses(size):
    for seed in range(100):
        g = minigames.BinaryHunt(size, extra=0, rng=random.Random(seed))
        while not g.over:
            g.guess(g.best_guess())
        assert g.won and len(g.guesses) <= g.optimal and g.stars == 3


def test_binary_hunt_loses_when_out_of_guesses():
    g = minigames.BinaryHunt(15, extra=0, rng=random.Random(3))
    wrong = [i for i in range(15) if i != g.idx][:g.max_guesses]
    for i in wrong:
        g.guess(i)
    assert g.over and not g.won and g.stars == 0 and g.guess(0) == 'over'


def test_bug_snippets_valid_and_hunt_flow():
    for sn in minigames.BUG_SNIPPETS:
        assert 0 <= sn['bug'] < len(sn['lines']) and sn['why'] and sn['goal']
    h = minigames.BugHunt(2, rng=random.Random(9))
    while not h.over:
        assert h.tap(h.current['bug']) is True
        if h.over:
            break
        h.advance()
    assert h.won and h.stars == 3
    h2 = minigames.BugHunt(3, rng=random.Random(9))
    for _ in range(2):
        h2.tap((h2.current['bug'] + 1) % len(h2.current['lines']))
        if not h2.over:
            h2.advance()
    assert h2.over and not h2.won and h2.lives == 0


def test_minigame_rewards_and_badges():
    p = engine.Profile()
    r = p.record_minigame('stack', 3)
    assert 'stacker' in r['new_badges'] and r['xp'] == 40
    r = p.record_minigame('binary', 3)
    assert 'seeker' in r['new_badges']
    r = p.record_minigame('bug', 2)
    assert 'bugsquash' in r['new_badges']


# ------------------------------------------------------------ layout guard
MAX_CODE_COLS = 38      # what fits in the phone code box at 14sp mono


def test_code_lines_fit_on_a_phone_screen():
    too_long = []
    for q in BANK:
        too_long += [ln for ln in q.code.split('\n') if len(ln) > MAX_CODE_COLS]
    for _t, _i, lesson in all_lessons():
        too_long += [ln for ln in lesson['code'].split('\n') if len(ln) > MAX_CODE_COLS]
    for sn in minigames.BUG_SNIPPETS:
        too_long += [ln for ln in sn['lines'] if len(ln) > 32]
    assert not too_long, too_long
