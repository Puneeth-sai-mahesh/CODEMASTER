"""Vibration feedback. Real vibration on Android, silently ignored everywhere else."""
from kivy.utils import platform

# Patterns are [wait, buzz, wait, buzz ...] in milliseconds.
PATTERNS = {
    'tap': [0, 12],
    'good': [0, 25, 45, 25],
    'bad': [0, 150],
    'win': [0, 40, 60, 40, 60, 140],
    'lose': [0, 90, 70, 200],
    'level': [0, 30, 40, 30, 40, 30, 40, 160],
}

enabled = True
_vibrator = None
_effect = None
_ready = False


def _setup():
    global _vibrator, _effect, _ready
    _ready = True
    if platform != 'android':
        return
    try:
        from jnius import autoclass
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        context = autoclass('android.content.Context')
        _vibrator = activity.getSystemService(context.VIBRATOR_SERVICE)
        if autoclass('android.os.Build$VERSION').SDK_INT >= 26:
            _effect = autoclass('android.os.VibrationEffect')
    except Exception:
        _vibrator = None


def play(kind='tap'):
    if not enabled:
        return
    if not _ready:
        _setup()
    if _vibrator is None:
        return
    pattern = PATTERNS.get(kind, PATTERNS['tap'])
    try:
        if _effect is not None:
            _vibrator.vibrate(_effect.createWaveform(pattern, -1))
        else:
            _vibrator.vibrate(pattern, -1)
    except Exception:
        try:                                    # fallback: one plain buzz of the same total length
            _vibrator.vibrate(int(sum(pattern[1::2])) or 20)
        except Exception:
            pass
