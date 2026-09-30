import pygame
from .round import Round
from .sounds import Sounds

# Game Engine

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (90, 90, 90)
GREEN = (40, 180, 90)
BLUE = (50, 90, 170)
RED = (190, 55, 55)
DARK = (28, 32, 44)
BUTTON = (44, 50, 66)
BUTTON_HOVER = (64, 74, 98)
LIGHT_GRAY = (170, 178, 196)
YELLOW = (240, 196, 70)

# rounds, min wait, max wait (ms)
DIFFICULTIES = {
    "Easy": (3, 1000, 2000),
    "Medium": (5, 1000, 3000),
    "Hard": (8, 1500, 5000),
}
LEVELS = ["Easy", "Medium", "Hard"]


class GameEngine:
    def __init__(self, width, height, rounds_total=5, min_wait_ms=1000, max_wait_ms=3000):
        self.width = width
        self.height = height

        self.rounds_total = rounds_total
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms
        self.difficulty = "Medium"

        self.round = None
        self.reaction_times = []
        self.false_starts = 0

        self.result_shown_at = None
        self.result_pause_ms = 800  # brief pause on the result screen between rounds
        self.false_start_pause_ms = 1200

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 46)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self.sounds = Sounds()

        # "menu", "playing" or "results"
        self.screen_state = "menu"
        self.game_over = False
        self.quit_requested = False
        self.buttons = []

    def start_session(self, level):
        self.difficulty = level
        self.rounds_total, self.min_wait_ms, self.max_wait_ms = DIFFICULTIES[level]
        self.reaction_times = []
        self.false_starts = 0
        self.game_over = False
        self.screen_state = "playing"
        self.round = Round(self.min_wait_ms, self.max_wait_ms)

    def end_session(self):
        self.game_over = True
        self.screen_state = "results"
        self.sounds.session_end.play()

    def handle_event(self, event):
        if self.screen_state != "playing":
            self.menu_event(event)
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.screen_state = "menu"
            return

        is_click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        is_space = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
        if not (is_click or is_space):
            return
        # ignore clicks while the result / false start screen is showing
        if self.round.state not in ("waiting", "go"):
            return

        reaction_ms = self.round.register_input()
        self.result_shown_at = pygame.time.get_ticks()
        if reaction_ms is None:
            self.false_starts += 1
            self.sounds.false_start.play()
        else:
            self.reaction_times.append(reaction_ms)

    def menu_event(self, event):
        # used for both the start menu and the results screen
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.quit_requested = True
            elif event.key in (pygame.K_1, pygame.K_e):
                self.start_session("Easy")
            elif event.key in (pygame.K_2, pygame.K_m):
                self.start_session("Medium")
            elif event.key in (pygame.K_3, pygame.K_h):
                self.start_session("Hard")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for label, rect in self.buttons:
                if rect.collidepoint(event.pos):
                    if label == "Exit":
                        self.quit_requested = True
                    else:
                        self.start_session(label)
                    break

    def handle_input(self):
        # Reserved for continuously-held-key input; every action here
        # is a discrete click/keypress, handled in handle_event.
        pass

    def update(self):
        if self.screen_state != "playing":
            return

        if self.round.update():
            self.sounds.go.play()

        now = pygame.time.get_ticks()
        if self.round.state == "result":
            if now - self.result_shown_at >= self.result_pause_ms:
                self._start_next_round()
        elif self.round.state == "false_start":
            # same round again with a new random wait
            if now - self.result_shown_at >= self.false_start_pause_ms:
                self.round = Round(self.min_wait_ms, self.max_wait_ms)

    def _start_next_round(self):
        if len(self.reaction_times) >= self.rounds_total:
            self.end_session()
            return
        self.round = Round(self.min_wait_ms, self.max_wait_ms)

    def average_reaction_ms(self):
        if not self.reaction_times:
            return 0
        return round(sum(self.reaction_times) / len(self.reaction_times))

    def render(self, screen):
        if self.screen_state == "menu":
            self.draw_menu(screen)
        elif self.screen_state == "results":
            self.draw_results(screen)
        else:
            self.draw_round(screen)

    def draw_text(self, screen, text, font, color, y):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(self.width // 2, y)))

    def draw_round(self, screen):
        if self.round.state == "waiting":
            bg = GRAY
            message = "Wait for green..."
        elif self.round.state == "go":
            bg = GREEN
            message = "Click now!"
        elif self.round.state == "false_start":
            bg = RED
            message = "Too soon! False start"
        else:
            bg = BLUE
            message = f"{self.round.reaction_ms} ms"

        screen.fill(bg)
        self.draw_text(screen, message, self.big_font, WHITE, self.height // 2)
        if self.round.state == "false_start":
            self.draw_text(screen, "Wait for green - this round will restart",
                           self.small_font, WHITE, self.height // 2 + 45)

        round_num = min(len(self.reaction_times) + 1, self.rounds_total)
        round_text = self.font.render(f"Round {round_num}/{self.rounds_total}", True, WHITE)
        screen.blit(round_text, (10, 10))

        avg_text = self.font.render(f"Avg: {self.average_reaction_ms()} ms", True, WHITE)
        screen.blit(avg_text, avg_text.get_rect(topright=(self.width - 10, 10)))

        info = f"{self.difficulty}  |  False starts: {self.false_starts}  |  Esc: menu"
        info_text = self.small_font.render(info, True, WHITE)
        screen.blit(info_text, info_text.get_rect(midbottom=(self.width // 2, self.height - 10)))

    def draw_buttons(self, screen, y):
        labels = LEVELS + ["Exit"]
        w, h, gap = 120, 44, 14
        x = (self.width - (len(labels) * w + (len(labels) - 1) * gap)) // 2
        mouse = pygame.mouse.get_pos() if pygame.mouse.get_focused() else (-1, -1)

        self.buttons = []
        for i, label in enumerate(labels):
            rect = pygame.Rect(x + i * (w + gap), y, w, h)
            if label == "Exit":
                color = RED
            elif rect.collidepoint(mouse):
                color = BUTTON_HOVER
            else:
                color = BUTTON
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, LIGHT_GRAY, rect, width=1, border_radius=10)
            txt = self.small_font.render(label, True, WHITE)
            screen.blit(txt, txt.get_rect(center=rect.center))
            self.buttons.append((label, rect))

        self.draw_text(screen, "Keys: 1 / 2 / 3 (or E / M / H) to play  -  Esc to exit",
                       self.small_font, LIGHT_GRAY, y + h + 22)

    def draw_menu(self, screen):
        screen.fill(DARK)
        self.draw_text(screen, "Reaction Time Tester", self.big_font, WHITE, 70)
        self.draw_text(screen, "Choose a difficulty", self.font, LIGHT_GRAY, 125)

        y = 165
        for level in LEVELS:
            rounds, lo, hi = DIFFICULTIES[level]
            self.draw_text(screen, f"{level}: {rounds} rounds, wait {lo / 1000:g}-{hi / 1000:g} s",
                           self.small_font, WHITE, y)
            y += 28

        self.draw_buttons(screen, 270)

    def draw_results(self, screen):
        screen.fill(DARK)
        self.draw_text(screen, f"Session complete - {self.difficulty}", self.font, WHITE, 32)

        # list all the times, 4 per column (hard mode has 8 so it needs 2 columns)
        best = min(self.reaction_times) if self.reaction_times else None
        cols = (len(self.reaction_times) + 3) // 4
        start_x = self.width // 2 - cols * 100
        for i, t in enumerate(self.reaction_times):
            color = YELLOW if t == best else WHITE
            txt = self.small_font.render(f"Round {i + 1}:  {t} ms", True, color)
            screen.blit(txt, (start_x + (i // 4) * 200 + 10, 66 + (i % 4) * 26))

        self.draw_text(screen, f"Average: {self.average_reaction_ms()} ms", self.big_font, YELLOW, 200)
        self.draw_text(screen, f"Best: {best} ms   |   False starts: {self.false_starts}",
                       self.small_font, LIGHT_GRAY, 240)

        self.draw_text(screen, "Play again?", self.small_font, WHITE, 272)
        self.draw_buttons(screen, 290)
