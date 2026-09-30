import math
from array import array

import pygame


def make_tone(freqs, length_ms, volume=0.5, square=False):
    # generates the beep in code so we don't need any .wav files
    rate, _, channels = pygame.mixer.get_init()
    samples = array("h")
    n = int(rate * length_ms / 1000 / len(freqs))
    fade = int(rate * 0.01)  # small fade so it doesn't click

    for f in freqs:
        for i in range(n):
            s = math.sin(2 * math.pi * f * i / rate)
            if square:
                s = 1 if s >= 0 else -1
            env = min(1, i / fade, (n - i) / fade)
            val = int(32767 * volume * env * s)
            for _ in range(channels):
                samples.append(val)

    return pygame.mixer.Sound(buffer=samples.tobytes())


class NoSound:
    def play(self):
        pass


class Sounds:
    def __init__(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 1, 512)
            self.go = make_tone([880], 120, 0.45)                       # short beep
            self.false_start = make_tone([160], 350, 0.35, square=True) # low buzz
            self.session_end = make_tone([523, 659, 784, 1047], 600, 0.4)  # little tune at the end
        except Exception:
            # no speakers / audio device -> just run without sound
            self.go = self.false_start = self.session_end = NoSound()
