"""Pure-Python game logic: quiz battles, XP/levels, badges and save data.

Nothing in here imports Kivy, so it can be unit-tested anywhere.
"""
import copy
import datetime
import json
import math
import os
import random

from lessons import all_lessons
from questions import BANK, TRACKS

DIFFS = {
    1: {'name': 'Easy', 'seconds': 30, 'lives': 5, 'count': 6, 'xp': 10},
    2: {'name': 'Medium', 'seconds': 22, 'lives': 4, 'count': 7, 'xp': 15},
    3: {'name': 'Hard', 'seconds': 16, 'lives': 3, 'count': 8, 'xp': 25},
}

RANKS = ['Rookie', 'Script Kid', 'Coder', 'Debugger', 'Hacker', 'Architect', 'Wizard', 'Legend']

BADGES = {
    'first_win': ('First Blood', 'Win your first quiz battle'),
    'perfect': ('Flawless', 'Earn 3 stars on any battle'),
    'combo5': ('On Fire', 'Answer 5 questions in a row correctly'),
    'tri_track': ('Triple Threat', 'Clear Easy in all three tracks'),
    'hard_win': ('Hard Mode', 'Win a Hard battle'),
    'streak3': ('Habit Builder', 'Play 3 days in a row'),
    'stacker': ('Stack Master', 'Solve a Stack Stacker puzzle'),
    'seeker': ('Binary Seeker', 'Find the number with a perfect binary search'),
    'bugsquash': ('Bug Squasher', 'Clear a Bug Hunter run'),
    'level5': ('Rising Star', 'Reach level 5'),
    'brainiac': ('Brainiac', 'Answer 100 questions correctly'),
    'bookworm': ('Bookworm', 'Read 10 lessons'),
}

HINT_PRICE = 15
DAILY_BONUS = 15
TOTAL_LESSONS = len(all_lessons())


# ---------------------------------------------------------------- levels
def level_for(xp):
    return int(math.sqrt(max(xp, 0) / 60.0)) + 1


def level_floor(level):
    return 60 * (level - 1) ** 2


def level_progress(xp):
    """(level, xp into this level, xp needed for this level)."""
    lvl = level_for(xp)
    lo, hi = level_floor(lvl), level_floor(lvl + 1)
    return lvl, xp - lo, hi - lo


def rank_for(level):
    return RANKS[min(level - 1, len(RANKS) - 1)]


# ---------------------------------------------------------------- quiz
class ShownQuestion:
    """A question with its options shuffled for this play-through."""

    def __init__(self, q, rng):
        opts = [q.correct] + list(q.wrong)
        rng.shuffle(opts)
        self.track = q.track
        self.text = q.text
        self.code = q.code
        self.lang = q.lang
        self.options = opts
        self.answer = opts.index(q.correct)
        self.why = q.why


class QuizSession:
    """One battle against a Bug Monster."""

    def __init__(self, track, diff, rng=None, questions=None, title=None, kind='quiz'):
        self.rng = rng or random.Random()
        self.track, self.diff, self.kind = track, diff, kind
        self.cfg = DIFFS[diff]
        if questions is None:
            pool = [q for q in BANK if q.track == track and q.diff == diff]
            questions = self.rng.sample(pool, min(self.cfg['count'], len(pool)))
        self.items = [ShownQuestion(q, self.rng) for q in questions]
        self.title = title or '%s - %s' % (TRACKS[track]['name'], self.cfg['name'])
        self.max_lives = self.lives = self.cfg['lives']
        self.index = 0
        self.combo = self.best_combo = 0
        self.correct = self.mistakes = self.xp = 0
        self.answered = False
        self.hint_used = False

    @property
    def current(self):
        return self.items[self.index]

    @property
    def total(self):
        return len(self.items)

    def use_hint(self):
        """Remove two wrong options. Returns the removed option indexes."""
        if self.answered or self.hint_used:
            return []
        wrong = [i for i in range(len(self.current.options)) if i != self.current.answer]
        self.rng.shuffle(wrong)
        self.hint_used = True
        return wrong[:2]

    def answer(self, choice, time_left=0.0):
        """choice=None means the timer ran out."""
        if self.answered:
            raise RuntimeError('question already answered')
        self.answered = True
        q = self.current
        ok = choice is not None and choice == q.answer
        gain = 0
        if ok:
            self.correct += 1
            self.combo += 1
            self.best_combo = max(self.best_combo, self.combo)
            mult = 1 + 0.2 * min(self.combo - 1, 5)
            frac = max(0.0, min(1.0, time_left / float(self.cfg['seconds'])))
            gain = round(self.cfg['xp'] * mult) + round(self.cfg['xp'] * 0.5 * frac)
            self.xp += gain
        else:
            self.mistakes += 1
            self.combo = 0
            self.lives -= 1
        return {'correct': ok, 'timeout': choice is None, 'xp': gain,
                'combo': self.combo, 'answer': q.answer, 'why': q.why}

    @property
    def is_last(self):
        return self.index >= self.total - 1

    @property
    def over(self):
        return self.lives <= 0 or (self.answered and self.is_last)

    @property
    def won(self):
        return self.lives > 0 and self.answered and self.is_last

    def advance(self):
        self.index += 1
        self.answered = False
        self.hint_used = False

    @property
    def stars(self):
        if not self.won:
            return 0
        acc = self.correct / float(self.total)
        return 3 if acc >= 0.999 else 2 if acc >= 0.75 else 1

    @property
    def coins(self):
        return self.correct + 5 * self.stars

    @property
    def monster_hp(self):
        return 1.0 - self.correct / float(self.total)


def daily_session(today=None):
    """Same six questions for everybody on a given day."""
    today = today or datetime.date.today()
    r = random.Random(today.toordinal())
    picks = []
    for track, diff in [('ds', 2), ('py', 2), ('c', 2), ('ds', 3), ('py', 3), ('c', 3)]:
        picks.append(r.choice([q for q in BANK if q.track == track and q.diff == diff]))
    r.shuffle(picks)
    return QuizSession('ds', 2, rng=r, questions=picks, title='Daily Challenge', kind='daily')


# ---------------------------------------------------------------- profile
DEFAULT_SAVE = {
    'xp': 0, 'coins': 20, 'hints': 3,
    'stars': {}, 'badges': [], 'lessons': [],
    'streak': 0, 'last_day': '', 'daily_done': '',
    'stats': {'battles': 0, 'wins': 0, 'correct': 0, 'best_combo': 0, 'perfects': 0,
              'hard_wins': 0, 'stack_wins': 0, 'seeker_perfect': 0, 'bug_wins': 0},
    'settings': {'sound': True, 'haptics': True},
}


def _merge(default, loaded):
    out = copy.deepcopy(default)
    for key, val in (loaded or {}).items():
        if key in out and isinstance(out[key], dict) and key in ('stats', 'settings'):
            out[key].update(val)
        else:
            out[key] = val
    return out


class Profile:
    def __init__(self, path=None):
        self.path = path
        self.data = copy.deepcopy(DEFAULT_SAVE)
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    self.data = _merge(DEFAULT_SAVE, json.load(fh))
            except (OSError, ValueError):
                self.data = copy.deepcopy(DEFAULT_SAVE)

    # ---- persistence
    def save(self):
        if not self.path:
            return
        try:
            tmp = self.path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as fh:
                json.dump(self.data, fh)
            os.replace(tmp, self.path)
        except OSError:
            pass

    def reset(self):
        self.data = copy.deepcopy(DEFAULT_SAVE)
        self.save()

    # ---- simple accessors
    @property
    def xp(self):
        return self.data['xp']

    @property
    def level(self):
        return level_for(self.data['xp'])

    @property
    def coins(self):
        return self.data['coins']

    @property
    def hints(self):
        return self.data['hints']

    @property
    def streak(self):
        return self.data['streak']

    def stars_for(self, track, diff):
        return self.data['stars'].get('%s-%d' % (track, diff), 0)

    def unlocked(self, track, diff):
        return diff == 1 or self.stars_for(track, diff - 1) >= 1

    def daily_available(self, today=None):
        today = today or datetime.date.today()
        return self.data['daily_done'] != today.isoformat()

    # ---- economy
    def buy_hint(self):
        if self.data['coins'] < HINT_PRICE:
            return False
        self.data['coins'] -= HINT_PRICE
        self.data['hints'] += 1
        self.save()
        return True

    def spend_hint(self):
        if self.data['hints'] <= 0:
            return False
        self.data['hints'] -= 1
        self.save()
        return True

    def _reward(self, xp, coins):
        before = self.level
        self.data['xp'] += xp
        self.data['coins'] += coins
        gained = self.level - before
        if gained > 0:
            self.data['hints'] += gained          # level-up gift
        return gained > 0

    def touch_day(self, today=None):
        today = today or datetime.date.today()
        iso = today.isoformat()
        if self.data['last_day'] == iso:
            return
        yesterday = (today - datetime.timedelta(days=1)).isoformat()
        self.data['streak'] = self.data['streak'] + 1 if self.data['last_day'] == yesterday else 1
        self.data['last_day'] = iso

    # ---- recording results
    def record_quiz(self, s, today=None):
        today = today or datetime.date.today()
        st = self.data['stats']
        self.touch_day(today)
        st['battles'] += 1
        st['correct'] += s.correct
        st['best_combo'] = max(st['best_combo'], s.best_combo)
        xp = s.xp
        coins = s.coins
        first_clear = False
        if s.won:
            st['wins'] += 1
            xp += 10 * s.diff
            if s.kind == 'quiz':
                st['perfects'] += 1 if s.stars == 3 else 0
                st['hard_wins'] += 1 if s.diff == 3 else 0
                key = '%s-%d' % (s.track, s.diff)
                first_clear = self.data['stars'].get(key, 0) == 0
                self.data['stars'][key] = max(self.data['stars'].get(key, 0), s.stars)
            else:
                if self.daily_available(today):
                    coins += DAILY_BONUS
                    self.data['daily_done'] = today.isoformat()
        elif s.kind == 'daily':
            pass
        leveled = self._reward(xp, coins)
        new = self.check_badges()
        self.save()
        return {'xp': xp, 'coins': coins, 'leveled': leveled, 'level': self.level,
                'new_badges': new, 'first_clear': first_clear}

    def record_minigame(self, game, stars, today=None):
        today = today or datetime.date.today()
        self.touch_day(today)
        st = self.data['stats']
        if stars > 0:
            key = {'stack': 'stack_wins', 'binary': None, 'bug': 'bug_wins'}[game]
            if key:
                st[key] += 1
            if game == 'binary' and stars == 3:
                st['seeker_perfect'] += 1
        xp = {0: 5, 1: 20, 2: 30, 3: 40}[stars]
        coins = stars * 4
        leveled = self._reward(xp, coins)
        new = self.check_badges()
        self.save()
        return {'xp': xp, 'coins': coins, 'leveled': leveled, 'level': self.level,
                'new_badges': new, 'first_clear': False}

    def mark_lesson(self, track, index):
        """First read of a lesson pays 5 XP. Returns the XP awarded."""
        key = '%s-%d' % (track, index)
        if key in self.data['lessons']:
            return 0
        self.data['lessons'].append(key)
        self.touch_day()
        self._reward(5, 0)
        self.check_badges()
        self.save()
        return 5

    # ---- badges
    def check_badges(self):
        d, s = self.data, self.data['stats']
        rules = {
            'first_win': s['wins'] >= 1,
            'perfect': s['perfects'] >= 1,
            'combo5': s['best_combo'] >= 5,
            'tri_track': all(self.stars_for(t, 1) >= 1 for t in TRACKS),
            'hard_win': s['hard_wins'] >= 1,
            'streak3': d['streak'] >= 3,
            'stacker': s['stack_wins'] >= 1,
            'seeker': s['seeker_perfect'] >= 1,
            'bugsquash': s['bug_wins'] >= 1,
            'level5': self.level >= 5,
            'brainiac': s['correct'] >= 100,
            'bookworm': len(d['lessons']) >= 10,
        }
        new = []
        for key, ok in rules.items():
            if ok and key not in d['badges']:
                d['badges'].append(key)
                new.append(key)
        return new
