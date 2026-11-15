"""Tiny synthesized sound effects. No audio assets needed: WAVs are generated on first run."""
import math
import os
import struct
import wave

RATE = 22050

# name -> list of (frequency Hz, milliseconds, wave shape)
SOUNDS = {
    'click': [(900, 35, 'sine')],
    'good': [(660, 80, 'sine'), (990, 150, 'sine')],
    'bad': [(180, 220, 'square')],
    'coin': [(1000, 60, 'sine'), (1500, 160, 'sine')],
    'win': [(523, 110, 'sine'), (659, 110, 'sine'), (784, 110, 'sine'), (1047, 320, 'sine')],
    'lose': [(392, 170, 'sine'), (330, 170, 'sine'), (262, 380, 'sine')],
    'level': [(523, 90, 'sine'), (659, 90, 'sine'), (784, 90, 'sine'), (1047, 90, 'sine'), (1319, 300, 'sine')],
    'tick': [(1200, 25, 'sine')],
}


def _samples(notes):
    out = []
    for freq, ms, shape in notes:
        n = int(RATE * ms / 1000.0)
        for i in range(n):
            t = i / float(RATE)
            ph = math.sin(2 * math.pi * freq * t)
            v = ph if shape == 'sine' else (0.6 if ph >= 0 else -0.6)
            attack = min(1.0, i / (RATE * 0.004))          # 4 ms fade-in removes clicks
            release = min(1.0, (n - i) / (RATE * 0.03))    # 30 ms fade-out
            out.append(v * attack * release * 0.45)
    return out


def _write(path, samples):
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, s)) * 32767)) for s in samples))


class Sfx:
    def __init__(self, folder):
        self.folder = folder
        self.enabled = True
        self._cache = {}
        try:
            os.makedirs(folder, exist_ok=True)
            for name, notes in SOUNDS.items():
                path = os.path.join(folder, name + '.wav')
                if not os.path.exists(path):
                    _write(path, _samples(notes))
        except OSError:
            self.enabled = False

    def play(self, name):
        if not self.enabled or name not in SOUNDS:
            return
        try:
            snd = self._cache.get(name)
            if snd is None:
                from kivy.core.audio import SoundLoader
                snd = SoundLoader.load(os.path.join(self.folder, name + '.wav'))
                self._cache[name] = snd
            if snd:
                snd.stop()
                snd.play()
        except Exception:
            pass          # audio must never crash the game
