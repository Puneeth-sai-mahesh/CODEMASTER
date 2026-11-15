"""Code Quest - learn Data Structures, Python and C by playing.

Run on a computer:  python main.py
Build an Android APK: see README.md (buildozer / GitHub Actions).
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.widget import Widget
from kivy.utils import platform

import haptics
from engine import (BADGES, DIFFS, HINT_PRICE, Profile, QuizSession, TOTAL_LESSONS,
                    daily_session, level_progress, rank_for)
from lessons import LESSONS
from minigames import BinaryHunt, BugHunt, StackPuzzle
from questions import TRACKS
from sfx import Sfx
from theme import (ACCENT, BAD, BG, DIFF_COLOR, DIM, GOLD, GOOD, MUTED, PANEL, PANEL2,
                   TEXT, TRACK_COLOR)
from widgets import (Bar, CodeBlock, Floaters, HeartRow, MonsterView, PillButton, RoundedBox,
                     StarRow, FONT_MONO, float_text, highlight, lbl)

DARK = (0.05, 0.07, 0.16, 1)
MONSTERS = ['Null Pointer', 'Memory Leak', 'Off-By-One', 'Stack Overflow', 'Infinite Loop',
            'Segfault', 'Syntax Error', 'Race Condition', 'Dangling Ptr', 'Dead Lock']
CHIP_COLORS = ['#2dd4bf', '#fbbf24', '#818cf8', '#fb7185', '#34d399', '#f472b6', '#38bdf8']


def chip_color(n):
    from kivy.utils import get_color_from_hex
    return get_color_from_hex(CHIP_COLORS[(n - 1) % len(CHIP_COLORS)])


# =========================================================================
# Base screen
# =========================================================================
class Base(Screen):
    back_to = None

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_bg, size=self._sync_bg)

    def _sync_bg(self, *_):
        self._bg.pos, self._bg.size = self.pos, self.size

    @property
    def app(self):
        return App.get_running_app()

    def column(self, spacing=10):
        box = BoxLayout(orientation='vertical', padding=[dp(14), dp(12), dp(14), dp(12)], spacing=dp(spacing))
        self.add_widget(box)
        return box

    def header(self, title, color=TEXT, right=None):
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        back = PillButton(text='<', size_hint_x=None, width=dp(48), fill=PANEL2, depth=dp(4))
        back.bind(on_release=lambda *_: self.app.go_back())
        row.add_widget(back)
        row.title = lbl(title, 22, color, bold=True)
        row.add_widget(row.title)
        if right is not None:
            row.add_widget(right)
        return row


def scroll_column(spacing=10):
    sv = ScrollView(do_scroll_x=False, bar_width=dp(3))
    col = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(spacing))
    col.bind(minimum_height=col.setter('height'))
    sv.add_widget(col)
    return sv, col


# =========================================================================
# Home
# =========================================================================
class HomeScreen(Base):
    def __init__(self, **kw):
        super().__init__(**kw)
        layer = FloatLayout()
        self.add_widget(layer)
        self.floaters = Floaters()
        layer.add_widget(self.floaters)
        box = BoxLayout(orientation='vertical', padding=[dp(18), dp(22), dp(18), dp(16)], spacing=dp(10))
        layer.add_widget(box)

        box.add_widget(lbl('[color=2dd4bf]CODE[/color] [color=fbbf24]QUEST[/color]', 46, bold=True,
                           halign='center', markup=True, size_hint_y=None, height=dp(62)))
        box.add_widget(lbl('Data Structures  |  Python  |  C', 14, MUTED, halign='center',
                           size_hint_y=None, height=dp(22)))
        box.add_widget(Widget(size_hint_y=None, height=dp(4)))

        card = RoundedBox(size_hint_y=None, height=dp(92), padding=dp(12), spacing=dp(12))
        ring = AnchorLayout(size_hint_x=None, width=dp(60))
        circle = RoundedBox(size_hint=(None, None), size=(dp(60), dp(60)), radius=dp(30), bg=PANEL2)
        self.lvl = lbl('1', 30, GOLD, bold=True, halign='center')
        circle.add_widget(self.lvl)
        ring.add_widget(circle)
        card.add_widget(ring)
        info = BoxLayout(orientation='vertical', spacing=dp(4))
        self.rank = lbl('', 18, TEXT, bold=True)
        self.xpbar = Bar(size_hint_y=None, height=dp(10), fill=ACCENT)
        self.stats = lbl('', 13, MUTED, markup=True)
        for w in (self.rank, self.xpbar, self.stats):
            info.add_widget(w)
        card.add_widget(info)
        box.add_widget(card)

        play = PillButton(text='PLAY QUEST', font_size='22sp', size_hint_y=None, height=dp(68), fill=ACCENT)
        play.bind(on_release=lambda *_: self.app.goto('quest'))
        box.add_widget(play)
        self.daily = PillButton(text='DAILY CHALLENGE', size_hint_y=None, height=dp(58), fill=TRACK_COLOR['daily'],
                                color=DARK)
        self.daily.bind(on_release=lambda *_: self.app.start_daily())
        box.add_widget(self.daily)
        for left, right in (('LEARN', 'MINI-GAMES'), ('TROPHIES', 'SETTINGS')):
            row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
            for text in (left, right):
                b = PillButton(text=text, fill=PANEL2)
                b.bind(on_release=lambda _b, t=text: self.app.goto({'LEARN': 'learn', 'MINI-GAMES': 'minis',
                                                                    'TROPHIES': 'trophies', 'SETTINGS': 'settings'}[t]))
                row.add_widget(b)
            box.add_widget(row)
        box.add_widget(Widget())

    def on_pre_enter(self, *_):
        p = self.app.profile
        lvl, into, need = level_progress(p.xp)
        self.lvl.text = str(lvl)
        self.rank.text = '%s  -  Level %d' % (rank_for(lvl), lvl)
        self.xpbar.value = into / float(need)
        self.stats.text = ('XP %d/%d    [color=fbbf24]Coins %d[/color]    Hints %d    Streak %dd'
                           % (into, need, p.coins, p.hints, p.streak))
        if p.daily_available():
            self.daily.text = 'DAILY CHALLENGE   +15 coins'
            self.daily.fill = TRACK_COLOR['daily']
        else:
            self.daily.text = 'DAILY CHALLENGE   done today'
            self.daily.fill = DIM

    def on_enter(self, *_):
        self.floaters.start()

    def on_leave(self, *_):
        self.floaters.stop()


# =========================================================================
# Quest map
# =========================================================================
class QuestScreen(Base):
    back_to = 'home'

    def __init__(self, **kw):
        super().__init__(**kw)
        box = self.column()
        box.add_widget(self.header('Choose your quest'))
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        self.info = lbl('', 15, MUTED, markup=True)
        self.buy = PillButton(text='Buy hint  %dc' % HINT_PRICE, size_hint_x=None, width=dp(140),
                              fill=GOLD, color=DARK, font_size='15sp')
        self.buy.bind(on_release=self.buy_hint)
        row.add_widget(self.info)
        row.add_widget(self.buy)
        box.add_widget(row)
        sv, self.list = scroll_column(12)
        box.add_widget(sv)

    def on_pre_enter(self, *_):
        self.refresh()

    def buy_hint(self, *_):
        if self.app.profile.buy_hint():
            self.app.feedback('coin')
            self.app.toast('Hint bought!')
        else:
            self.app.feedback('bad')
            self.app.toast('Not enough coins - win battles to earn more')
        self.refresh()

    def refresh(self):
        p = self.app.profile
        self.info.text = '[color=fbbf24]%d coins[/color]   %d hints' % (p.coins, p.hints)
        self.list.clear_widgets()
        for track in TRACKS:
            self.list.add_widget(self.track_card(track))

    def track_card(self, track):
        p, col = self.app.profile, TRACK_COLOR[track]
        card = RoundedBox(orientation='vertical', size_hint_y=None, height=dp(176), padding=dp(14), spacing=dp(6))
        card.add_widget(lbl(TRACKS[track]['name'], 21, col, bold=True, size_hint_y=None, height=dp(28)))
        card.add_widget(lbl(TRACKS[track]['tag'], 13, MUTED, size_hint_y=None, height=dp(20)))
        row = BoxLayout(spacing=dp(10))
        for diff in (1, 2, 3):
            ok = p.unlocked(track, diff)
            cell = BoxLayout(orientation='vertical', spacing=dp(2))
            btn = PillButton(text=DIFFS[diff]['name'] if ok else 'Locked', fill=DIFF_COLOR[diff] if ok else DIM,
                             color=DARK if ok else MUTED, disabled=not ok, disabled_color=MUTED, font_size='15sp')
            btn.bind(on_release=lambda _b, t=track, d=diff: self.app.start_quiz(t, d))
            cell.add_widget(btn)
            cell.add_widget(StarRow(count=p.stars_for(track, diff), size_hint_y=None, height=dp(22)))
            row.add_widget(cell)
        card.add_widget(row)
        return card


# =========================================================================
# Quiz battle
# =========================================================================
class QuizScreen(Base):
    back_to = 'quest'

    def __init__(self, **kw):
        super().__init__(**kw)
        self.s = None
        self.time_left = self.time_total = 1.0
        self.running = False
        self._ev = None
        self.stage = FloatLayout()
        self.add_widget(self.stage)
        self.shaker = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(8),
                                size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        self.stage.add_widget(self.shaker)
        box = self.shaker

        top = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        back = PillButton(text='<', size_hint_x=None, width=dp(46), fill=PANEL2, depth=dp(4))
        back.bind(on_release=lambda *_: self.app.go_back())
        self.title_lbl = lbl('', 15, MUTED)
        self.hearts = HeartRow(size_hint_x=None, width=dp(140))
        for w in (back, self.title_lbl, self.hearts):
            top.add_widget(w)
        box.add_widget(top)

        self.timer = Bar(size_hint_y=None, height=dp(10))
        box.add_widget(self.timer)

        arena = BoxLayout(size_hint_y=0.30, spacing=dp(10))
        self.monster = MonsterView(size_hint_x=0.5)
        side = BoxLayout(orientation='vertical', spacing=dp(4), padding=[0, dp(8), 0, dp(8)])
        self.mname = lbl('', 17, TEXT, bold=True)
        self.hp = Bar(size_hint_y=None, height=dp(12), fill=BAD)
        self.qcount = lbl('', 14, MUTED)
        self.combo = lbl('', 20, GOLD, bold=True)
        for w in (self.mname, self.hp, self.qcount, self.combo):
            side.add_widget(w)
        arena.add_widget(self.monster)
        arena.add_widget(side)
        box.add_widget(arena)

        self.card = RoundedBox(orientation='vertical', padding=dp(12), size_hint_y=0.40)
        sv, self.qbox = scroll_column(10)
        self.q_lbl = lbl('', 18, TEXT, bold=True, wrap=True)
        self.code = CodeBlock('', '')
        self.qbox.add_widget(self.q_lbl)
        self.card.add_widget(sv)
        box.add_widget(self.card)

        self.opts = []
        optbox = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(4 * 50 + 3 * 8), spacing=dp(8))
        for i in range(4):
            b = PillButton(text='', fill=PANEL2, font_size='15sp', disabled_color=(1, 1, 1, .9), depth=dp(4))
            b.bind(on_release=lambda _b, i=i: self.choose(i))
            self.opts.append(b)
            optbox.add_widget(b)
        box.add_widget(optbox)

        self.footer = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(112), spacing=dp(6))
        box.add_widget(self.footer)

    # ---- lifecycle
    def start(self, session, back='quest'):
        self.s, self.back_to = session, back
        self.col = TRACK_COLOR['daily' if session.kind == 'daily' else session.track]
        self.monster.color = self.col
        self.monster.mood = 'idle'
        self.mname.text = random.choice(MONSTERS)
        self.mname.color = self.col
        self.title_lbl.text = session.title
        self.hearts.max_lives = session.max_lives
        self.hearts.lives = session.lives
        self.hp.value = 1.0
        self.combo.text = ''
        self.show_question()

    def on_pre_enter(self, *_):
        self.monster.start()

    def on_enter(self, *_):
        if self._ev is None:
            self._ev = Clock.schedule_interval(self.tick, 1 / 30.0)

    def on_leave(self, *_):
        self.running = False
        self.monster.stop()
        if self._ev is not None:
            self._ev.cancel()
            self._ev = None

    # ---- question flow
    def show_question(self):
        s, q = self.s, self.s.current
        self.q_lbl.text = q.text
        if q.code:
            self.code.set_code(q.code, q.lang)
            if self.code.parent is None:
                self.qbox.add_widget(self.code)
        elif self.code.parent is not None:
            self.qbox.remove_widget(self.code)
        for b, text in zip(self.opts, q.options):
            b.text, b.fill, b.disabled, b.color, b.opacity = text, PANEL2, False, TEXT, 1
        self.qcount.text = 'Question %d / %d' % (s.index + 1, s.total)
        self.time_total = self.time_left = float(s.cfg['seconds'])
        self.timer.value = 1.0
        self.timer.fill = GOOD
        self.running = True
        self.show_pre()

    def show_pre(self):
        self.footer.clear_widgets()
        row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        self.hint_btn = PillButton(text='HINT  (%d)' % self.app.profile.hints, fill=GOLD, color=DARK,
                                   size_hint_x=0.5, font_size='16sp', depth=dp(4))
        self.hint_btn.bind(on_release=self.use_hint)
        row.add_widget(self.hint_btn)
        row.add_widget(lbl('Answer fast for bonus XP', 13, MUTED, halign='center'))
        self.footer.add_widget(row)
        self.footer.add_widget(Widget())

    def tick(self, dt):
        if not self.running or self.s is None:
            return
        self.time_left -= dt
        frac = max(0.0, self.time_left / self.time_total)
        self.timer.value = frac
        self.timer.fill = GOOD if frac > .5 else GOLD if frac > .25 else BAD
        if self.time_left <= 0:
            self.choose(None)

    def use_hint(self, *_):
        if self.s.answered or self.s.hint_used:
            return
        if not self.app.profile.spend_hint():
            self.app.feedback('bad')
            self.app.toast('No hints left - buy some on the quest map')
            return
        for i in self.s.use_hint():
            self.opts[i].disabled = True
            self.opts[i].fill = DIM
            self.opts[i].opacity = .35
        self.hint_btn.text = 'HINT  (%d)' % self.app.profile.hints
        self.hint_btn.fill = DIM

    def choose(self, idx):
        s = self.s
        if s is None or s.answered:
            return
        self.running = False
        res = s.answer(idx, max(0.0, self.time_left))
        for i, b in enumerate(self.opts):
            b.disabled = True
            if i == res['answer']:
                b.fill = GOOD
                b.color = DARK
            elif i == idx:
                b.fill = BAD
            else:
                b.fill = DIM
                b.opacity = .5
        self.hearts.lives = s.lives
        self.hp.value = s.monster_hp
        cx, cy = self.monster.center_x, self.monster.center_y
        if res['correct']:
            self.app.feedback('good')
            self.monster.hit()
            float_text(self.stage, '+%d XP' % res['xp'], cx, cy, GOLD)
            self.combo.text = 'COMBO x%d' % res['combo'] if res['combo'] >= 2 else ''
            head = '[color=34d399][b]Correct![/b][/color] '
        else:
            self.app.feedback('bad')
            self.app.shake(self.shaker)
            self.combo.text = ''
            head = ('[color=fb7185][b]Time is up![/b][/color] ' if res['timeout']
                    else '[color=fb7185][b]Not quite.[/b][/color] ')
        if s.won:
            self.monster.mood = 'dead'
        self.show_post(head + res['why'])

    def show_post(self, text):
        self.footer.clear_widgets()
        box = RoundedBox(padding=dp(10), radius=dp(12))
        sv = ScrollView(do_scroll_x=False, bar_width=dp(2))
        sv.add_widget(lbl(text, 14, TEXT, wrap=True, markup=True))
        box.add_widget(sv)
        self.footer.add_widget(box)
        nxt = PillButton(text='FINISH' if self.s.over else 'NEXT', size_hint_y=None, height=dp(46),
                         fill=ACCENT, depth=dp(4))
        nxt.bind(on_release=self.next)
        self.footer.add_widget(nxt)

    def next(self, *_):
        if self.s.over:
            self.app.finish_quiz(self.s)
        else:
            self.s.advance()
            self.show_question()


# =========================================================================
# Result screen (used by quizzes and mini-games)
# =========================================================================
class ResultScreen(Base):
    back_to = 'home'

    def __init__(self, **kw):
        super().__init__(**kw)
        self.box = self.column(8)

    def show(self, info):
        """info: title, subtitle, win, stars, rows[(label, value, color)], badges, level_up, note, buttons."""
        self.back_to = info.get('back', 'home')
        box = self.box
        box.clear_widgets()
        win = info['win']
        box.add_widget(Widget(size_hint_y=0.4))
        box.add_widget(lbl(info['title'], 40, GOOD if win else BAD, bold=True, halign='center',
                           size_hint_y=None, height=dp(52)))
        box.add_widget(lbl(info.get('subtitle', ''), 15, MUTED, halign='center', wrap=True))
        stars = StarRow(size_hint_y=None, height=dp(72), count=0, lit=0)
        box.add_widget(stars)
        card = RoundedBox(orientation='vertical', size_hint_y=None, padding=dp(14), spacing=dp(6))
        for label, value, color in info.get('rows', []):
            r = BoxLayout(size_hint_y=None, height=dp(26))
            r.add_widget(lbl(label, 16, MUTED))
            r.add_widget(lbl(value, 17, color, bold=True, halign='right'))
            card.add_widget(r)
        card.height = dp(28) * len(info.get('rows', [])) + dp(28)
        box.add_widget(card)
        for bid in info.get('badges', []):
            name, desc = BADGES[bid]
            box.add_widget(lbl('[color=fbbf24][b]New badge: %s[/b][/color]  %s' % (name, desc), 14, TEXT,
                               halign='center', wrap=True, markup=True))
        if info.get('level_up'):
            box.add_widget(lbl('[color=7c5cff][b]LEVEL UP![/b][/color]  You are now level %d  (+1 hint)'
                               % info['level_up'], 16, TEXT, halign='center', wrap=True, markup=True))
        if info.get('note'):
            box.add_widget(lbl(info['note'], 13, MUTED, halign='center', wrap=True))
        box.add_widget(Widget(size_hint_y=0.6))
        for text, cb, fill in info['buttons']:
            b = PillButton(text=text, size_hint_y=None, height=dp(54), fill=fill)
            b.bind(on_release=lambda _b, cb=cb: cb())
            box.add_widget(b)
        app = self.app
        app.feedback('win' if win else 'lose')
        if win and info.get('stars'):
            stars.reveal(info['stars'], on_star=lambda i: app.feedback('coin'))
        if info.get('level_up'):
            Clock.schedule_once(lambda dt: app.feedback('level'), 1.4)


# =========================================================================
# Learn
# =========================================================================
class LearnScreen(Base):
    back_to = 'home'

    def __init__(self, **kw):
        super().__init__(**kw)
        box = self.column()
        box.add_widget(self.header('Learn'))
        self.prog = lbl('', 14, MUTED, size_hint_y=None, height=dp(22))
        box.add_widget(self.prog)
        sv, self.list = scroll_column(8)
        box.add_widget(sv)

    def on_pre_enter(self, *_):
        done = self.app.profile.data['lessons']
        self.prog.text = 'Lessons read: %d / %d   (+5 XP the first time you read one)' % (len(done), TOTAL_LESSONS)
        self.list.clear_widgets()
        for track, items in LESSONS.items():
            self.list.add_widget(lbl(TRACKS[track]['name'], 18, TRACK_COLOR[track], bold=True,
                                     size_hint_y=None, height=dp(32)))
            for i, lesson in enumerate(items):
                read = '%s-%d' % (track, i) in done
                row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
                b = PillButton(text=lesson['title'], fill=PANEL2, font_size='16sp', depth=dp(4))
                b.bind(on_release=lambda _b, t=track, i=i: self.app.open_lesson(t, i))
                row.add_widget(b)
                row.add_widget(lbl('READ' if read else '+5 XP', 12, GOOD if read else GOLD, bold=True,
                                   halign='center', size_hint_x=None, width=dp(54)))
                self.list.add_widget(row)


class LessonScreen(Base):
    back_to = 'learn'

    def __init__(self, **kw):
        super().__init__(**kw)
        box = self.column()
        self.head = self.header('')
        box.add_widget(self.head)
        self.sub = lbl('', 14, MUTED, size_hint_y=None, height=dp(22))
        box.add_widget(self.sub)
        sv, self.body = scroll_column(12)
        self.text = lbl('', 16, TEXT, wrap=True)
        self.code = CodeBlock('', '')
        self.body.add_widget(self.text)
        self.body.add_widget(self.code)
        box.add_widget(sv)
        row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
        self.prev = PillButton(text='PREVIOUS', fill=PANEL2)
        self.nxt = PillButton(text='NEXT', fill=ACCENT)
        self.prev.bind(on_release=lambda *_: self.step(-1))
        self.nxt.bind(on_release=lambda *_: self.step(1))
        row.add_widget(self.prev)
        row.add_widget(self.nxt)
        box.add_widget(row)
        self.track, self.idx = 'ds', 0

    def open(self, track, idx):
        self.track, self.idx = track, idx
        items = LESSONS[track]
        lesson = items[idx]
        col = TRACK_COLOR[track]
        self.head.title.text, self.head.title.color = lesson['title'], col
        self.sub.text = '%s   -   lesson %d of %d' % (TRACKS[track]['name'], idx + 1, len(items))
        self.text.text = lesson['body']
        self.code.set_code(lesson['code'], 'py' if track in ('ds', 'py') else 'c')
        self.prev.disabled = idx == 0
        self.prev.fill = DIM if idx == 0 else PANEL2
        self.nxt.disabled = idx == len(items) - 1
        self.nxt.fill = DIM if idx == len(items) - 1 else ACCENT
        self.nxt.disabled_color = MUTED
        self.prev.disabled_color = MUTED
        if self.app.profile.mark_lesson(track, idx):
            self.app.toast('+5 XP for reading!')
            self.app.feedback('coin')

    def step(self, d):
        self.open(self.track, self.idx + d)


# =========================================================================
# Mini-games hub
# =========================================================================
class MinisScreen(Base):
    back_to = 'home'
    GAMES = [
        ('stack', 'Stack Stacker', 'Push and pop numbers to build the target output. Learn LIFO.', 'ds'),
        ('binary', 'Binary Hunt', 'Find the hidden number in as few guesses as possible. Learn binary search.', 'py'),
        ('bug', 'Bug Hunter', 'Tap the broken line of Python / C code before you run out of lives.', 'c'),
    ]

    def __init__(self, **kw):
        super().__init__(**kw)
        box = self.column(12)
        box.add_widget(self.header('Mini-games'))
        sv, col = scroll_column(12)
        for key, title, desc, track in self.GAMES:
            card = RoundedBox(orientation='vertical', size_hint_y=None, height=dp(168), padding=dp(14), spacing=dp(6))
            card.add_widget(lbl(title, 21, TRACK_COLOR[track], bold=True, size_hint_y=None, height=dp(28)))
            card.add_widget(lbl(desc, 14, MUTED, wrap=True))
            row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
            for diff in (1, 2, 3):
                b = PillButton(text=DIFFS[diff]['name'], fill=DIFF_COLOR[diff], color=DARK, font_size='15sp', depth=dp(4))
                b.bind(on_release=lambda _b, k=key, d=diff: self.app.start_mini(k, d))
                row.add_widget(b)
            card.add_widget(row)
            col.add_widget(card)
        box.add_widget(sv)


# =========================================================================
# Mini-game 1: Stack Stacker
# =========================================================================
class StackScreen(Base):
    back_to = 'minis'
    SIZE = {1: 4, 2: 5, 3: 6}

    def __init__(self, **kw):
        super().__init__(**kw)
        self.diff, self.g = 1, None
        box = self.column(8)
        box.add_widget(self.header('Stack Stacker', TRACK_COLOR['ds']))
        box.add_widget(lbl('Numbers arrive in order 1, 2, 3 ... PUSH puts the next one on the stack, '
                           'POP moves the TOP item to the output. Build the TARGET.', 13, MUTED, wrap=True))
        self.target_row = self._row(box, 'TARGET')
        self.input_row = self._row(box, 'INPUT')
        box.add_widget(lbl('STACK  (last in, first out)', 12, MUTED, size_hint_y=None, height=dp(18)))
        self.well = RoundedBox(radius=dp(14), bg=PANEL)
        self.anchor = AnchorLayout(anchor_x='center', anchor_y='bottom', padding=dp(6))
        self.stack_col = BoxLayout(orientation='vertical', size_hint=(None, None), width=dp(64), spacing=dp(3))
        self.anchor.add_widget(self.stack_col)
        self.well.add_widget(self.anchor)
        box.add_widget(self.well)
        self.output_row = self._row(box, 'OUTPUT')
        self.msg = lbl('', 14, GOLD, halign='center', size_hint_y=None, height=dp(24))
        box.add_widget(self.msg)
        r1 = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        self.push_b = PillButton(text='PUSH  v', fill=TRACK_COLOR['ds'], color=DARK)
        self.pop_b = PillButton(text='POP  ^', fill=TRACK_COLOR['py'], color=DARK)
        self.push_b.bind(on_release=self.do_push)
        self.pop_b.bind(on_release=self.do_pop)
        r1.add_widget(self.push_b)
        r1.add_widget(self.pop_b)
        box.add_widget(r1)
        r2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        self.reset_b = PillButton(text='RESET', fill=PANEL2, font_size='15sp', depth=dp(4))
        self.hint_b = PillButton(text='HINT', fill=GOLD, color=DARK, font_size='15sp', depth=dp(4))
        self.reset_b.bind(on_release=self.do_reset)
        self.hint_b.bind(on_release=self.do_hint)
        r2.add_widget(self.reset_b)
        r2.add_widget(self.hint_b)
        box.add_widget(r2)

    def _row(self, box, title):
        box.add_widget(lbl(title, 12, MUTED, size_hint_y=None, height=dp(18)))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        box.add_widget(row)
        return row

    def _chips(self, row, items):
        row.clear_widgets()
        for n in items:
            row.add_widget(self._chip(n))
        row.add_widget(Widget())

    def _chip(self, n):
        c = RoundedBox(size_hint=(None, None), size=(dp(44), dp(40)), bg=chip_color(n), radius=dp(10))
        c.add_widget(lbl(str(n), 20, DARK, bold=True, halign='center'))
        return c

    def start(self, diff):
        self.diff = diff
        self.g = StackPuzzle(self.SIZE[diff])
        self.render('Tip: the number you pushed LAST comes off FIRST.')

    def render(self, msg=None):
        g = self.g
        self._chips(self.target_row, g.target)
        self._chips(self.input_row, g.inp)
        self._chips(self.output_row, g.out)
        self.stack_col.clear_widgets()
        for n in reversed(g.stack):
            self.stack_col.add_widget(self._chip(n))
        self.stack_col.height = max(dp(1), len(g.stack) * dp(43))
        if msg is not None:
            self.msg.text = msg
        self.reset_b.fill = GOLD if g.dead else PANEL2
        self.reset_b.color = DARK if g.dead else TEXT

    def do_push(self, *_):
        if self.g.push():
            if self.g.dead:
                self.app.feedback('bad')
                self.render('Dead end! That order blocks the target - press RESET.')
            else:
                self.render('')
        else:
            self.app.feedback('bad')
            self.msg.text = 'Nothing left to push.'

    def do_pop(self, *_):
        res = self.g.pop()
        if res == 'ok':
            self.app.feedback('good')
            self.render('')
            if self.g.solved:
                Clock.schedule_once(lambda dt: self.app.finish_stack(self.g, self.diff), 0.7)
        elif res == 'wrong':
            self.app.feedback('bad')
            self.app.shake(self.well)
            self.render('The TOP item is not the next one the target needs.')
        else:
            self.app.feedback('bad')
            self.msg.text = 'The stack is empty - PUSH first.'

    def do_reset(self, *_):
        self.g.reset()
        self.render('Fresh start - same target.')

    def do_hint(self, *_):
        move = self.g.next_move()
        if move is None:
            self.msg.text = 'No safe move - press RESET.'
            return
        if not self.app.profile.spend_hint():
            self.app.feedback('bad')
            self.app.toast('No hints left')
            return
        self.msg.text = 'Hint: press %s' % move.upper()
        btn = self.push_b if move == 'push' else self.pop_b
        anim = Animation(opacity=.3, d=.2) + Animation(opacity=1, d=.2)
        anim.repeat = False
        (anim + anim).start(btn)


# =========================================================================
# Mini-game 2: Binary Hunt
# =========================================================================
class BinaryScreen(Base):
    back_to = 'minis'
    CFG = {1: (15, 2, 5), 2: (31, 1, 6), 3: (63, 0, 8)}      # size, extra guesses, columns

    def __init__(self, **kw):
        super().__init__(**kw)
        self.g, self.diff, self.cells = None, 1, []
        box = self.column(8)
        box.add_widget(self.header('Binary Hunt', TRACK_COLOR['py']))
        self.find = lbl('', 34, GOLD, bold=True, halign='center', size_hint_y=None, height=dp(48))
        self.left = lbl('', 15, TEXT, halign='center', size_hint_y=None, height=dp(24))
        self.msg = lbl('', 14, MUTED, halign='center', wrap=True)
        box.add_widget(self.find)
        box.add_widget(self.left)
        box.add_widget(self.msg)
        self.grid = GridLayout(cols=5, spacing=dp(6), size_hint_y=None)
        self.grid.bind(width=self._size_grid, minimum_height=self.grid.setter('height'))
        sv = ScrollView(do_scroll_x=False, bar_width=dp(2))
        sv.add_widget(self.grid)
        box.add_widget(sv)
        self.hint_b = PillButton(text='HINT: show the middle', fill=GOLD, color=DARK, size_hint_y=None,
                                 height=dp(48), font_size='15sp', depth=dp(4))
        self.hint_b.bind(on_release=self.do_hint)
        box.add_widget(self.hint_b)

    def _size_grid(self, *_):
        cols = self.grid.cols
        cell = (self.grid.width - dp(6) * (cols - 1)) / cols
        self.grid.row_default_height = cell
        self.grid.row_force_default = True

    def start(self, diff):
        self.diff = diff
        size, extra, cols = self.CFG[diff]
        self.g = BinaryHunt(size, extra)
        self.grid.cols = cols
        self.grid.clear_widgets()
        self.cells = []
        for i in range(size):
            b = PillButton(text='?', fill=PANEL2, font_size='15sp', depth=dp(3), radius=dp(10), feedback='tick')
            b.bind(on_release=lambda _b, i=i: self.tap(i))
            self.cells.append(b)
            self.grid.add_widget(b)
        self._size_grid()
        self.find.text = 'FIND  %d' % self.g.target
        self.msg.text = ('The numbers are SORTED. Tap a cell to open it. Tip: always open the MIDDLE '
                         'of the cells that are still bright.')
        self.hint_b.text = 'HINT: show the middle'
        self.refresh()

    def refresh(self):
        g = self.g
        self.left.text = 'Guesses left: %d   (a perfect search needs %d)' % (g.left, g.optimal)
        for i, b in enumerate(self.cells):
            if i in g.guesses:
                b.text = str(g.values[i])
                b.fill = GOOD if g.values[i] == g.target else (PANEL if not g.in_range(i) else DIM)
                b.color = DARK if g.values[i] == g.target else MUTED
            else:
                b.text = '?'
                b.fill = PANEL2 if g.in_range(i) else PANEL
                b.color = TEXT if g.in_range(i) else MUTED

    def tap(self, i):
        g = self.g
        res = g.guess(i)
        if res in ('over', 'repeat'):
            return
        self.refresh()
        if res == 'found':
            self.app.feedback('good')
            Clock.schedule_once(lambda dt: self.app.finish_binary(g, self.diff), 0.7)
        elif res == 'low':
            self.msg.text = '%d is too SMALL. The target is to the RIGHT -> ' % g.values[i]
        else:
            self.msg.text = '%d is too BIG. The target is to the LEFT <- ' % g.values[i]
        if res != 'found':
            self.app.feedback('bad')
            if g.over:
                Clock.schedule_once(lambda dt: self.app.finish_binary(g, self.diff), 0.7)

    def do_hint(self, *_):
        g = self.g
        if g.over:
            return
        if not self.app.profile.spend_hint():
            self.app.feedback('bad')
            self.app.toast('No hints left')
            return
        mid = g.best_guess()
        self.cells[mid].fill = GOLD
        self.cells[mid].color = DARK
        self.msg.text = 'The middle of the bright cells is #%d. Open it!' % (mid + 1)


# =========================================================================
# Mini-game 3: Bug Hunter
# =========================================================================
class LineRow(ButtonBehavior, RoundedBox):
    pass


class BugScreen(Base):
    back_to = 'minis'

    def __init__(self, **kw):
        super().__init__(**kw)
        self.g, self.diff, self.rows = None, 1, []
        self.hearts = HeartRow(size_hint_x=None, width=dp(110))
        box = self.column(8)
        box.add_widget(self.header('Bug Hunter', TRACK_COLOR['c'], right=self.hearts))
        self.round = lbl('', 14, MUTED, size_hint_y=None, height=dp(22))
        self.goal = lbl('', 17, TEXT, bold=True, wrap=True)
        box.add_widget(self.round)
        box.add_widget(self.goal)
        sv, self.lines = scroll_column(6)
        box.add_widget(sv)
        self.footer = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(6))
        box.add_widget(self.footer)

    def start(self, diff):
        self.diff = diff
        self.g = BugHunt(diff)
        self.hearts.max_lives = self.g.max_lives
        self.hearts.lives = self.g.lives
        self.show_round()

    def show_round(self):
        g, sn = self.g, self.g.current
        self.round.text = 'Bug %d / %d      %s' % (g.index + 1, g.total, 'Python' if sn['lang'] == 'py' else 'C')
        self.goal.text = 'Goal: ' + sn['goal']
        self.lines.clear_widgets()
        self.rows = []
        for i, text in enumerate(sn['lines']):
            row = LineRow(size_hint_y=None, height=dp(42), padding=[dp(10), 0, dp(6), 0], radius=dp(10), bg=PANEL)
            row.add_widget(lbl(str(i + 1), 13, MUTED, mono=True, size_hint_x=None, width=dp(24)))
            row.add_widget(lbl(highlight(text, sn['lang']), 14, TEXT, mono=True, markup=True))
            row.bind(on_release=lambda _r, i=i: self.tap(i))
            self.rows.append(row)
            self.lines.add_widget(row)
        self.footer.clear_widgets()
        self.footer.add_widget(lbl('Tap the line that contains the bug.', 14, MUTED, halign='center'))

    def tap(self, i):
        g, sn = self.g, self.g.current
        ok = g.tap(i)
        if ok is None:
            return
        self.hearts.lives = g.lives
        self.rows[sn['bug']].bg = [0.2, 0.83, 0.6, 0.35]
        if ok:
            self.app.feedback('good')
        else:
            self.rows[i].bg = [0.98, 0.44, 0.52, 0.35]
            self.app.feedback('bad')
            self.app.shake(self.lines.parent)
        self.footer.clear_widgets()
        head = '[color=34d399][b]Bug found![/b][/color] ' if ok else '[color=fb7185][b]Not that line.[/b][/color] '
        box = RoundedBox(padding=dp(10), radius=dp(12))
        sv = ScrollView(do_scroll_x=False, bar_width=dp(2))
        sv.add_widget(lbl(head + sn['why'], 14, TEXT, wrap=True, markup=True))
        box.add_widget(sv)
        self.footer.add_widget(box)
        nxt = PillButton(text='FINISH' if g.over else 'NEXT BUG', size_hint_y=None, height=dp(46), depth=dp(4))
        nxt.bind(on_release=self.next)
        self.footer.add_widget(nxt)

    def next(self, *_):
        if self.g.over:
            self.app.finish_bug(self.g, self.diff)
        else:
            self.g.advance()
            self.show_round()


# =========================================================================
# Trophies + settings
# =========================================================================
class TrophiesScreen(Base):
    back_to = 'home'

    def __init__(self, **kw):
        super().__init__(**kw)
        box = self.column()
        box.add_widget(self.header('Trophies'))
        sv, self.list = scroll_column(8)
        box.add_widget(sv)

    def on_pre_enter(self, *_):
        p = self.app.profile
        st = p.data['stats']
        self.list.clear_widgets()
        card = RoundedBox(orientation='vertical', size_hint_y=None, height=dp(150), padding=dp(14), spacing=dp(2))
        lvl = p.level
        for text in ('Level %d  -  %s' % (lvl, rank_for(lvl)), 'Total XP: %d' % p.xp,
                     'Battles won: %d / %d' % (st['wins'], st['battles']),
                     'Correct answers: %d    Best combo: x%d' % (st['correct'], st['best_combo']),
                     'Day streak: %d' % p.streak):
            card.add_widget(lbl(text, 15, TEXT if text.startswith('Level') else MUTED,
                                bold=text.startswith('Level')))
        self.list.add_widget(card)
        got = set(p.data['badges'])
        self.list.add_widget(lbl('Badges  %d / %d' % (len(got), len(BADGES)), 18, GOLD, bold=True,
                                 size_hint_y=None, height=dp(32)))
        for key, (name, desc) in BADGES.items():
            earned = key in got
            row = RoundedBox(orientation='vertical', size_hint_y=None, height=dp(62), padding=[dp(14), dp(8)],
                             bg=PANEL2 if earned else PANEL)
            row.add_widget(lbl(name if earned else 'Locked: ' + name, 16, GOLD if earned else MUTED, bold=True))
            row.add_widget(lbl(desc, 13, TEXT if earned else DIM))
            self.list.add_widget(row)


class SettingsScreen(Base):
    back_to = 'home'

    def __init__(self, **kw):
        super().__init__(**kw)
        self.armed = False
        box = self.column(12)
        box.add_widget(self.header('Settings'))
        self.sound = PillButton(text='', size_hint_y=None, height=dp(58), fill=PANEL2)
        self.vib = PillButton(text='', size_hint_y=None, height=dp(58), fill=PANEL2)
        self.reset = PillButton(text='', size_hint_y=None, height=dp(54), fill=PANEL2)
        self.sound.bind(on_release=lambda *_: self.toggle('sound'))
        self.vib.bind(on_release=lambda *_: self.toggle('haptics'))
        self.reset.bind(on_release=self.reset_progress)
        for w in (self.sound, self.vib, self.reset):
            box.add_widget(w)
        box.add_widget(lbl('Code Quest teaches Data Structures, Python and C.\n'
                           'Answers are checked by running real code. Progress is saved on this device.',
                           13, MUTED, wrap=True))
        box.add_widget(Widget())

    def on_pre_enter(self, *_):
        self.armed = False
        self.refresh()

    def refresh(self):
        s = self.app.profile.data['settings']
        self.sound.text = 'Sound effects:  %s' % ('ON' if s['sound'] else 'OFF')
        self.sound.fill = GOOD if s['sound'] else DIM
        self.sound.color = DARK if s['sound'] else TEXT
        self.vib.text = 'Haptics (vibration):  %s' % ('ON' if s['haptics'] else 'OFF')
        self.vib.fill = GOOD if s['haptics'] else DIM
        self.vib.color = DARK if s['haptics'] else TEXT
        self.reset.text = 'Tap again to ERASE all progress' if self.armed else 'Reset progress'
        self.reset.fill = BAD if self.armed else PANEL2

    def toggle(self, key):
        s = self.app.profile.data['settings']
        s[key] = not s[key]
        self.app.profile.save()
        self.app.apply_settings()
        self.app.feedback('tap')
        self.refresh()

    def reset_progress(self, *_):
        if not self.armed:
            self.armed = True
            self.refresh()
            return
        self.app.profile.reset()
        self.app.apply_settings()
        self.armed = False
        self.refresh()
        self.app.toast('Progress erased')


# =========================================================================
# The app
# =========================================================================
class CodeQuestApp(App):
    title = 'Code Quest'

    def build(self):
        Window.clearcolor = BG
        self.profile = Profile(os.path.join(self.user_data_dir, 'save.json'))
        self.sfx = Sfx(os.path.join(self.user_data_dir, 'sfx'))
        self.apply_settings()
        root = FloatLayout()
        self.layer = root
        self.sm = ScreenManager(transition=SlideTransition(duration=0.2))
        self.screens = {}
        for name, cls in (('home', HomeScreen), ('quest', QuestScreen), ('quiz', QuizScreen),
                          ('result', ResultScreen), ('learn', LearnScreen), ('lesson', LessonScreen),
                          ('minis', MinisScreen), ('stack', StackScreen), ('binary', BinaryScreen),
                          ('bug', BugScreen), ('trophies', TrophiesScreen), ('settings', SettingsScreen)):
            scr = cls(name=name)
            self.screens[name] = scr
            self.sm.add_widget(scr)
        root.add_widget(self.sm)
        Window.bind(on_keyboard=self.on_key)
        return root

    # ---- plumbing
    def apply_settings(self):
        s = self.profile.data['settings']
        self.sfx.enabled = s['sound']
        haptics.enabled = s['haptics']

    def feedback(self, kind):
        self.sfx.play({'tap': 'click'}.get(kind, kind))
        if kind != 'tick':
            haptics.play(kind)

    def goto(self, name, direction='left'):
        self.sm.transition.direction = direction
        self.sm.current = name

    def go_back(self):
        cur = self.sm.current_screen
        target = cur.back_to
        if target:
            self.goto(target, 'right')
            return True
        return False

    def on_key(self, window, key, *args):
        if key == 27:                       # Android back button / Esc
            return self.go_back()
        return False

    def on_pause(self):
        self.profile.save()
        return True

    def on_stop(self):
        self.profile.save()

    def toast(self, text):
        box = RoundedBox(size_hint=(None, None), size=(dp(300), dp(44)), bg=PANEL2, radius=dp(22),
                         pos_hint={'center_x': .5, 'top': .93})
        box.add_widget(lbl(text, 14, TEXT, halign='center'))
        self.layer.add_widget(box)
        anim = Animation(opacity=1, d=0) + Animation(opacity=1, d=1.4) + Animation(opacity=0, d=.4)
        anim.bind(on_complete=lambda *_: self.layer.remove_widget(box))
        anim.start(box)

    def shake(self, widget):
        """Visual 'haptic': wiggle a widget that lives in a FloatLayout/pos_hint parent."""
        parent = widget.parent
        if parent is None:
            return
        base_x = widget.x
        offsets = [14, -12, 9, -7, 4, -2, 0]
        for n, off in enumerate(offsets):
            Clock.schedule_once(lambda dt, off=off: self._nudge(widget, base_x, off), 0.035 * n)

    def _nudge(self, widget, base_x, off):
        if widget.parent is None:
            return
        widget.x = base_x + dp(off)
        if off == 0 and widget.pos_hint and 'x' in widget.pos_hint:
            widget.parent.do_layout()

    # ---- starting things
    def start_quiz(self, track, diff):
        self.screens['quiz'].start(QuizSession(track, diff), back='quest')
        self.goto('quiz')

    def start_daily(self):
        if not self.profile.daily_available():
            self.toast('Daily challenge already done - come back tomorrow!')
            self.feedback('bad')
            return
        self.screens['quiz'].start(daily_session(), back='home')
        self.goto('quiz')

    def open_lesson(self, track, idx):
        self.screens['lesson'].open(track, idx)
        self.goto('lesson')

    def start_mini(self, game, diff):
        self.screens[game].start(diff)
        self.goto(game)

    # ---- finishing things
    def _result(self, info):
        self.screens['result'].show(info)
        self.goto('result')

    def finish_quiz(self, s):
        res = self.profile.record_quiz(s)
        win = s.won
        back = 'home' if s.kind == 'daily' else 'quest'
        again = self.start_daily if s.kind == 'daily' else (lambda: self.start_quiz(s.track, s.diff))
        buttons = []
        if win and s.kind == 'quiz' and s.diff < 3:
            buttons.append(('NEXT LEVEL', lambda: self.start_quiz(s.track, s.diff + 1), ACCENT))
        if not (s.kind == 'daily' and win):
            buttons.append(('TRY AGAIN' if not win else 'PLAY AGAIN', again, PANEL2 if buttons else ACCENT))
        buttons.append(('BACK', lambda: self.goto(back, 'right'), PANEL2))
        self._result({
            'title': 'VICTORY!' if win else 'DEFEATED', 'win': win, 'stars': s.stars, 'back': back,
            'subtitle': (s.title + ' cleared.') if win else 'The bug monster survived. Read the Learn section and strike back!',
            'rows': [('Correct answers', '%d / %d' % (s.correct, s.total), TEXT),
                     ('Best combo', 'x%d' % s.best_combo, GOLD),
                     ('XP earned', '+%d' % res['xp'], ACCENT),
                     ('Coins earned', '+%d' % res['coins'], GOLD)],
            'badges': res['new_badges'], 'level_up': res['level'] if res['leveled'] else None,
            'buttons': buttons[:3],
        })

    def _mini_result(self, game, stars, res, title, subtitle, rows, note, again, back='minis'):
        win = stars > 0
        self._result({
            'title': title, 'win': win, 'stars': stars, 'subtitle': subtitle, 'back': back,
            'rows': rows + [('XP earned', '+%d' % res['xp'], ACCENT), ('Coins earned', '+%d' % res['coins'], GOLD)],
            'badges': res['new_badges'], 'level_up': res['level'] if res['leveled'] else None, 'note': note,
            'buttons': [('PLAY AGAIN', again, ACCENT), ('BACK', lambda: self.goto(back, 'right'), PANEL2)],
        })

    def finish_stack(self, g, diff):
        res = self.profile.record_minigame('stack', g.stars)
        self._mini_result('stack', g.stars, res, 'SOLVED!', 'You produced the target sequence.',
                          [('Moves', str(g.moves), TEXT), ('Slips', str(g.mistakes + g.resets), GOLD)],
                          'A stack is LIFO: the last item pushed is the first one popped.',
                          lambda: self.start_mini('stack', diff))

    def finish_binary(self, g, diff):
        stars = g.stars
        res = self.profile.record_minigame('binary', stars)
        title = 'FOUND IT!' if g.won else 'OUT OF GUESSES'
        self._mini_result('binary', stars, res, title,
                          'The number %d was in cell #%d.' % (g.target, g.idx + 1),
                          [('Guesses used', '%d  (best %d)' % (len(g.guesses), g.optimal), TEXT)],
                          'Binary search halves the search space every step: n items need about log2(n) guesses.',
                          lambda: self.start_mini('binary', diff))

    def finish_bug(self, g, diff):
        res = self.profile.record_minigame('bug', g.stars)
        title = 'BUGS SQUASHED!' if g.won else 'THE BUGS WIN'
        self._mini_result('bug', g.stars, res, title,
                          'You found %d of %d bugs.' % (g.found, g.total),
                          [('Wrong taps', str(g.mistakes), GOLD)],
                          'Read the code line by line and compare it with the goal - that is how debugging works.',
                          lambda: self.start_mini('bug', diff))


if __name__ == '__main__':
    if platform in ('win', 'linux', 'macosx'):
        Window.size = (405, 780)
    CodeQuestApp().run()
