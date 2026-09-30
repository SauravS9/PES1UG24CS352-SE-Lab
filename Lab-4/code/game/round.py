import random
import pygame


class Round:
    def __init__(self, min_wait_ms=1000, max_wait_ms=3000):
        self.wait_delay_ms = random.randint(min_wait_ms, max_wait_ms)
        self.state = "waiting"  # waiting -> go -> result   (or waiting -> false_start)
        self.start_time = pygame.time.get_ticks()
        self.go_time = None
        self.reaction_ms = None

    def update(self):
        # returns True only on the frame it turns green (used to play the beep)
        if self.state == "waiting":
            now = pygame.time.get_ticks()
            if now - self.start_time >= self.wait_delay_ms:
                self.state = "go"
                self.go_time = now
                return True
        return False

    def register_input(self):
        # clicked while still grey = false start, don't record it
        if self.state == "waiting":
            self.state = "false_start"
            return None

        if self.state == "go":
            now = pygame.time.get_ticks()
            # earlier this used start_time so the wait time was getting added to every result
            self.reaction_ms = now - self.go_time
            self.state = "result"
            return self.reaction_ms

        # round already over, ignore extra clicks
        return None
