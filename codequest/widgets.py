"""Reusable Kivy widgets: buttons, bars, hearts, stars, the Bug Monster, code blocks."""
import math
import os
import random
import re

import kivy
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Mesh, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from theme import ACCENT, BAD, CODE_BG, DIM, GOLD, GOOD, MUTED, PANEL, TEXT, TRACK_COLOR

_mono = os.path.join(kivy.kivy_data_dir, 'fonts', 'RobotoMono-Regular.ttf')
FONT_MONO = _mono if os.path.exists(_mono) else 'Roboto'

Builder.load_string('''
<RoundedBox>:
    canvas.before:
        Color:
            rgba: self.bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.radius]

<PillButton>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    bold: True
    font_size: '17sp'
    color: 0.96, 0.97, 1, 1
    halign: 'center'
    valign: 'middle'
    text_size: self.width - dp(16), self.height
    padding: [0, 0, 0, 0 if self.state == 'down' else self.depth]
    canvas.before:
        Color:
            rgba: self.shadow
        RoundedRectangle:
            pos: self.x, self.y
            size: self.width, self.height - self.depth
            radius: [self.radius]
        Color:
            rgba: self.fill
        RoundedRectangle:
            pos: self.x, self.y + (0 if self.state == 'down' else self.depth)
            size: self.width, self.height - self.depth
            radius: [self.radius]

<Bar>:
    canvas:
        Color:
            rgba: self.track
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2.0]
        Color:
            rgba: self.fill
        RoundedRectangle:
            pos: self.pos
            size: (max(self.height, self.width * min(1.0, max(0.0, self.value))) if self.value > 0.004 else 0), self.height
            radius: [self.height / 2.0]
''')


# ------------------------------------------------------------------ basics
class RoundedBox(BoxLayout):
    bg = ListProperty(PANEL)
    radius = NumericProperty(dp(18))


class PillButton(Button):
    fill = ListProperty(ACCENT)
    shadow = ListProperty([0.2, 0.15, 0.5, 1])
    depth = NumericProperty(dp(5))
    radius = NumericProperty(dp(16))
    feedback = StringProperty('tap')

    def __init__(self, **kw):
        super().__init__(**kw)
        self._sync_shadow()
        self.bind(fill=self._sync_shadow)

    def _sync_shadow(self, *_):
        f = self.fill
        self.shadow = [f[0] * .55, f[1] * .55, f[2] * .55, f[3] if len(f) > 3 else 1]

    def on_press(self):
        app = App.get_running_app()
        if app is not None and hasattr(app, 'feedback') and self.feedback:
            app.feedback(self.feedback)


class Bar(Widget):
    value = NumericProperty(1.0)
    fill = ListProperty(GOOD)
    track = ListProperty(DIM)


def lbl(text='', size=16, color=TEXT, bold=False, halign='left', valign='middle',
        wrap=False, mono=False, **kw):
    """Label factory. wrap=True makes the label as tall as its text (for scroll views)."""
    label = Label(text=text, font_size=sp(size), color=color, bold=bold,
                  halign=halign, valign=valign, **kw)
    if mono:
        label.font_name = FONT_MONO
    if wrap:
        label.size_hint_y = None
        label.bind(width=lambda w, v: setattr(w, 'text_size', (v, None)),
                   texture_size=lambda w, v: setattr(w, 'height', v[1] + dp(2)))
    else:
        label.bind(size=lambda w, v: setattr(w, 'text_size', v))
    return label


# ------------------------------------------------------------ vector shapes
def _fan(center, points):
    verts = [center[0], center[1], 0, 0]
    for x, y in list(points) + [points[0]]:
        verts += [x, y, 0, 0]
    Mesh(vertices=verts, indices=list(range(len(verts) // 4)), mode='triangle_fan')


def heart_points(cx, cy, size, n=28):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * size / 34.0, cy + (y + 2.5) * size / 34.0))
    return pts


def star_points(cx, cy, r, inner=0.45):
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * inner
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    return pts


class HeartRow(Widget):
    lives = NumericProperty(3)
    max_lives = NumericProperty(3)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._trig = Clock.create_trigger(self.redraw, -1)
        self.bind(pos=self._trig, size=self._trig, lives=self._trig, max_lives=self._trig)
        self._trig()

    def redraw(self, *_):
        self.canvas.clear()
        n = max(1, int(self.max_lives))
        step = min(self.width / n, self.height * 1.1)
        size = step * 0.82
        x0 = self.x + step / 2
        with self.canvas:
            for i in range(n):
                Color(*(BAD if i < self.lives else DIM))
                cx = x0 + i * step
                _fan((cx, self.center_y), heart_points(cx, self.center_y, size))


class StarRow(Widget):
    """Three stars; `count` are earned and `lit` of them are currently shown as gold."""
    count = NumericProperty(0)
    lit = NumericProperty(3)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._trig = Clock.create_trigger(self.redraw, -1)
        self.bind(pos=self._trig, size=self._trig, count=self._trig, lit=self._trig)
        self._trig()

    def redraw(self, *_):
        self.canvas.clear()
        step = min(self.width / 3.0, self.height * 1.15)
        r = step * 0.46
        x0 = self.center_x - step
        with self.canvas:
            for i in range(3):
                on = i < min(self.count, self.lit)
                Color(*(GOLD if on else DIM))
                cx = x0 + i * step
                _fan((cx, self.center_y), star_points(cx, self.center_y, r))

    def reveal(self, count, on_star=None):
        """Animate stars lighting up one by one."""
        self.count = count
        self.lit = 0

        def step(i):
            self.lit = i
            if on_star:
                on_star(i)
        for i in range(1, count + 1):
            Clock.schedule_once(lambda dt, i=i: step(i), 0.45 * i)


# ------------------------------------------------------------ Bug Monster
class MonsterView(Widget):
    color = ListProperty(TRACK_COLOR['ds'])
    flash = NumericProperty(0)
    t = NumericProperty(0)
    mood = StringProperty('idle')        # idle | dead | happy

    def __init__(self, **kw):
        super().__init__(**kw)
        self._ev = None
        self.bind(pos=self.redraw, size=self.redraw, color=self.redraw,
                  flash=self.redraw, t=self.redraw, mood=self.redraw)

    def start(self):
        if self._ev is None:
            self._ev = Clock.schedule_interval(self._tick, 1 / 30.0)

    def stop(self):
        if self._ev is not None:
            self._ev.cancel()
            self._ev = None

    def _tick(self, dt):
        self.t += dt

    def hit(self):
        Animation.cancel_all(self, 'flash')
        self.flash = 1.0
        Animation(flash=0, d=0.4).start(self)

    def redraw(self, *_):
        c = self.canvas
        c.clear()
        s = min(self.width, self.height)
        if s <= 0:
            return
        dead = self.mood == 'dead'
        bob = 0 if dead else math.sin(self.t * 2.4) * s * 0.03
        cx, cy = self.center_x, self.center_y + bob
        bw, bh = s * 0.70, s * 0.56
        r, g, b = self.color[:3]
        alpha = 0.45 if dead else 1.0
        with c:
            # legs
            Color(r * .5, g * .5, b * .5, alpha)
            for side in (-1, 1):
                for k in (-1, 0, 1):
                    wiggle = 0 if dead else math.sin(self.t * 5 + k + side) * s * 0.02
                    Line(points=[cx + side * bw * .40, cy + k * bh * .2 - bh * .06,
                                 cx + side * bw * .68, cy + k * bh * .34 - bh * .12 + wiggle],
                         width=dp(2.4))
            # antennae
            for side in (-1, 1):
                ax, ay = cx + side * bw * .34, cy + bh * .62 + (0 if dead else math.sin(self.t * 3 + side) * s * .02)
                Line(points=[cx + side * bw * .16, cy + bh * .42, ax, ay], width=dp(2.2))
                Ellipse(pos=(ax - s * .045, ay - s * .045), size=(s * .09, s * .09))
            # body
            Color(r, g, b, alpha)
            RoundedRectangle(pos=(cx - bw / 2, cy - bh / 2), size=(bw, bh), radius=[bh * .45])
            Color(1, 1, 1, .16 * alpha)
            Ellipse(pos=(cx - bw * .36, cy + bh * .1), size=(bw * .3, bh * .2))
            if self.flash > 0:
                Color(1, 1, 1, self.flash * .85)
                RoundedRectangle(pos=(cx - bw / 2, cy - bh / 2), size=(bw, bh), radius=[bh * .45])
            # eyes
            er = bh * .17
            for side in (-1, 1):
                ex, ey = cx + side * bw * .2, cy + bh * .08
                if dead:
                    Color(.1, .1, .2, 1)
                    d = er * .8
                    Line(points=[ex - d, ey - d, ex + d, ey + d], width=dp(2.2))
                    Line(points=[ex - d, ey + d, ex + d, ey - d], width=dp(2.2))
                elif self.flash > .25:
                    Color(.1, .1, .2, 1)
                    Line(points=[ex - er, ey, ex + er, ey], width=dp(2.6))
                else:
                    Color(1, 1, 1, 1)
                    Ellipse(pos=(ex - er, ey - er), size=(er * 2, er * 2))
                    Color(.08, .08, .18, 1)
                    px = math.sin(self.t * 1.3) * er * .35
                    Ellipse(pos=(ex - er * .5 + px, ey - er * .5), size=(er, er))
            # mouth
            Color(.1, .1, .2, 1)
            my = cy - bh * .2
            if dead:
                Line(points=[cx - bw * .12, my, cx + bw * .12, my], width=dp(2.2))
            elif self.mood == 'happy':
                Line(points=[cx - bw * .14, my + bh * .04, cx - bw * .06, my - bh * .06,
                             cx + bw * .06, my - bh * .06, cx + bw * .14, my + bh * .04], width=dp(2.2))
            else:
                pts = []
                for i in range(7):
                    pts += [cx - bw * .15 + i * bw * .05, my + (bh * .05 if i % 2 else -bh * .03)]
                Line(points=pts, width=dp(2.2))


# ------------------------------------------------------------ code display
_PY_KW = set('def return if else elif for while in import from class yield not and or is None True False '
             'lambda try except with as pass break continue'.split())
_C_KW = set('int char float double void if else for while return struct sizeof NULL const unsigned long '
            'short break continue include'.split())
_TOK = {
    'py': re.compile(r'(?P<com>#.*)|(?P<str>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|(?P<num>\b\d+(?:\.\d+)?\b)|(?P<id>[A-Za-z_]\w*)'),
    'c': re.compile(r'(?P<com>//.*)|(?P<pre>^#\w+)|(?P<str>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|(?P<num>\b\d+(?:\.\d+)?\b)|(?P<id>[A-Za-z_]\w*)', re.M),
}


def _esc(s):
    return s.replace('&', '&amp;').replace('[', '&bl;').replace(']', '&br;')


def highlight(code, lang):
    """Return Kivy markup with simple syntax colors."""
    if lang not in _TOK:
        return _esc(code)
    kws = _PY_KW if lang == 'py' else _C_KW
    out, pos = [], 0
    for m in _TOK[lang].finditer(code):
        out.append(_esc(code[pos:m.start()]))
        text, kind = m.group(0), m.lastgroup
        col = {'com': '7b86c9', 'str': '34d399', 'num': 'fbbf24', 'pre': 'c084fc'}.get(kind)
        if kind == 'id':
            col = 'c084fc' if text in kws else None
        out.append('[color=%s]%s[/color]' % (col, _esc(text)) if col else _esc(text))
        pos = m.end()
    out.append(_esc(code[pos:]))
    return ''.join(out)


class CodeBlock(RoundedBox):
    """Dark box with syntax-highlighted monospace code; sizes itself to the text."""

    def __init__(self, code='', lang='', size=14, **kw):
        super().__init__(orientation='vertical', padding=dp(12), size_hint_y=None, **kw)
        self.bg = CODE_BG
        self.radius = dp(12)
        self.label = Label(text=highlight(code, lang), markup=True, font_name=FONT_MONO,
                           font_size=sp(size), color=TEXT, halign='left', valign='top', size_hint_y=None)
        self.label.bind(width=lambda w, v: setattr(w, 'text_size', (v, None)),
                        texture_size=lambda w, v: setattr(w, 'height', v[1]))
        self.label.bind(height=lambda w, v: setattr(self, 'height', v + dp(24)))
        self.add_widget(self.label)

    def set_code(self, code, lang=''):
        self.label.text = highlight(code, lang)


# ------------------------------------------------------------ small effects
class Floaters(FloatLayout):
    """Faint code symbols drifting upward behind the home screen."""
    WORDS = ['{ }', '[ ]', '*p', 'def', 'O(n)', 'int', 'push', 'pop', 'NULL', '->', 'for', '0x1F',
             'malloc', 'yield', 'stack', 'queue', 'i++', '&x', 'O(1)', 'tree', 'hash']

    def start(self, count=14, tries=0):
        self.stop()
        if self.height < Window.height * 0.5 and tries < 25:     # layout not finished yet
            Clock.schedule_once(lambda dt: self.start(count, tries + 1), 0.1)
            return
        for _ in range(count):
            word = random.choice(self.WORDS)
            col = random.choice(list(TRACK_COLOR.values()))
            item = Label(text=word, font_size=sp(random.choice([14, 18, 24, 30])), bold=True,
                         color=(col[0], col[1], col[2], 0.13), size_hint=(None, None), font_name=FONT_MONO)
            item.texture_update()
            item.size = item.texture_size
            item.x = random.uniform(self.x, max(self.x, self.right - item.width))
            item.y = random.uniform(self.y, self.top)
            self.add_widget(item)
            self._drift(item)

    def _drift(self, item):
        if item.parent is None:
            return
        dur = random.uniform(14, 30)
        left = max(0.15, (self.top - item.y) / max(1.0, self.height))
        anim = Animation(y=self.top + dp(10), d=dur * left)

        def again(*_):
            if item.parent is not None:
                item.y = self.y - item.height
                item.x = random.uniform(self.x, max(self.x, self.right - item.width))
                self._drift(item)
        anim.bind(on_complete=again)
        anim.start(item)

    def stop(self):
        for child in list(self.children):
            Animation.cancel_all(child)
            self.remove_widget(child)


def float_text(parent, text, x, y, color=GOLD, size=22):
    """Pop-up text that drifts up and fades (e.g. '+14 XP')."""
    item = lbl(text, size, color, bold=True, halign='center', size_hint=(None, None))
    item.size = (dp(160), dp(36))
    item.center_x, item.y = x, y
    parent.add_widget(item)
    anim = Animation(y=y + dp(70), opacity=0, d=1.0, t='out_quad')
    anim.bind(on_complete=lambda *_: parent.remove_widget(item))
    anim.start(item)
