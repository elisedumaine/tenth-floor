"""Sound: the game's sound effects, made from waves in code (no sound files). Its owner is in OWNERS.md.

    from engine import sound
    sound.play("ding")

Names: jump, tick, found, nothing, caught, ding, locked, win, lose, zap, alarm, lunge.
If the computer has no sound (or the check runs with none), every call quietly does nothing.
"""
import math
import random
from array import array

import pygame

RATE = 22050
_sounds = {}
_ready = None            # None = not tried yet, False = no sound on this machine


def _tone(freq, secs, wave="square", vol=0.35, slide=0.0, decay=6.0):
    """One note: freq in Hz, sliding by `slide` Hz over its length, fading out at `decay`."""
    n = int(RATE * secs)
    out, phase = [], 0.0
    for i in range(n):
        t = i / RATE
        f = freq + slide * (i / n)
        phase += 2 * math.pi * f / RATE
        if wave == "square":
            v = 1.0 if math.sin(phase) >= 0 else -1.0
        elif wave == "noise":
            v = random.uniform(-1, 1)
        else:
            v = math.sin(phase) + 0.4 * math.sin(2.01 * phase)       # a bell: two partials
        out.append(v * vol * math.exp(-decay * t))
    return out


def _seq(*parts):
    return [s for p in parts for s in p]


def _build():
    random.seed(7)
    rest = lambda secs: [0.0] * int(RATE * secs)
    return {
        "jump": _tone(330, 0.12, slide=330, decay=10),
        "tick": _tone(1200, 0.03, vol=0.15, decay=40),
        "found": _seq(_tone(660, 0.08), _tone(880, 0.08), _tone(1320, 0.18, decay=8)),
        "nothing": _seq(_tone(260, 0.09, vol=0.25), _tone(200, 0.14, vol=0.25)),
        "caught": _seq(_tone(0, 0.12, wave="noise", vol=0.4, decay=12), _tone(440, 0.4, slide=-330, decay=4)),
        "ding": _tone(988, 0.7, wave="bell", vol=0.3, decay=5),
        "locked": _tone(110, 0.3, vol=0.3, decay=3),
        "win": _seq(_tone(523, 0.12), _tone(659, 0.12), _tone(784, 0.12), rest(0.04), _tone(1047, 0.5, decay=3)),
        "lose": _seq(_tone(392, 0.2), _tone(330, 0.2), _tone(262, 0.6, decay=3)),
        "zap": _tone(0, 0.25, wave="noise", vol=0.3, decay=8),
        "alarm": _seq(_tone(880, 0.07, vol=0.2), _tone(660, 0.07, vol=0.2)),
        "lunge": _tone(200, 0.2, slide=400, vol=0.25, decay=6),
    }


def _init():
    global _ready
    if _ready is not None:
        return _ready
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(RATE, -16, 1, 512)
        freq, _size, channels = pygame.mixer.get_init()
        for name, samples in _build().items():
            if freq != RATE:                                   # the mixer runs at another rate: resample simply
                step = RATE / freq
                samples = [samples[int(i * step)] for i in range(int(len(samples) / step))]
            pcm = array("h", (int(max(-1.0, min(1.0, s)) * 32767) for s in samples for _ in range(channels)))
            _sounds[name] = pygame.mixer.Sound(buffer=pcm.tobytes())
        _ready = True
    except Exception:                                          # no audio device: play nothing, never crash
        _ready = False
    return _ready


def play(name):
    """Play one effect by name. Unknown names and machines without sound do nothing."""
    if _init() and name in _sounds:
        _sounds[name].play()
