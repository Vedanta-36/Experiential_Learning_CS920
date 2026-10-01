import random
import pygame
from game.text_box import TextBox


class GameEngine:
    QUESTION_TIME_LIMIT = 10.0

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.score = 0
        self.total_attempts = 0
        self.streak = 0
        self.multiplier = 1
        self.feedback_msg = "Solve the card and press Enter!"
        self.feedback_color = (200, 205, 215)

        self.num_a = 0
        self.num_b = 0
        self.operator = "+"
        self.question_started_at = 0
        self.timed_out = False

        box_w, box_h = 130, 44
        self.input_box = TextBox(width // 2 - 110, 230, box_w, box_h)
        self.submit_btn = pygame.Rect(width // 2 + 30, 230, 90, box_h)

        self.font_title = pygame.font.SysFont(None, 38)
        self.font_hud = pygame.font.SysFont(None, 26)
        self.font_card = pygame.font.SysFont(None, 56)
        self.font_btn = pygame.font.SysFont(None, 24)
        self.font_timer = pygame.font.SysFont(None, 22)

        self.generate_new_card()

    def generate_new_card(self):
        self.operator = random.choice(["+", "-", "*", "/"])

        if self.operator == "/":
            # Generate divisor and quotient first so the dividend is always
            # exactly divisible by the divisor (no remainder).
            self.num_b = random.randint(2, 12)
            quotient = random.randint(2, 15)
            self.num_a = self.num_b * quotient
        else:
            self.num_a = random.randint(3, 15)
            self.num_b = random.randint(2, 12)
            if self.operator == "-" and self.num_a < self.num_b:
                self.num_a, self.num_b = self.num_b, self.num_a

        self.input_box.clear()
        self.question_started_at = pygame.time.get_ticks()
        self.timed_out = False

    def compute_expected_answer(self):
        """Return the mathematical result for the current flashcard."""
        if self.operator == "+":
            return self.num_a + self.num_b
        if self.operator == "-":
            return self.num_a - self.num_b
        if self.operator == "*":
            return self.num_a * self.num_b
        if self.operator == "/":
            # Cards are generated with an exact divisor, so // is appropriate.
            return self.num_a // self.num_b
        raise ValueError(f"Unsupported operator: {self.operator}")

    def _reset_streak(self):
        self.streak = 0
        self.multiplier = 1

    def _record_correct_answer(self):
        self.streak += 1
        if self.streak >= 5:
            self.multiplier = 3
        elif self.streak >= 3:
            self.multiplier = 2
        else:
            self.multiplier = 1

    def submit_answer(self):
        # A timeout is handled by update() before normal input can be submitted.
        if self.timed_out:
            return

        val_str = self.input_box.text.strip()
        if not val_str or val_str == "-":
            self.feedback_msg = "Type an answer first!"
            self.feedback_color = (240, 175, 40)
            return

        # TextBox accepts only digits and an optional leading '-'. Keep this
        # guard so submit_answer remains safe if called with invalid text by
        # another caller or a future input widget.
        try:
            user_answer = int(val_str)
        except ValueError:
            self.feedback_msg = "Enter a valid integer!"
            self.feedback_color = (240, 175, 40)
            return

        expected = self.compute_expected_answer()
        self.total_attempts += 1

        if user_answer == expected:
            self._record_correct_answer()
            earned_points = self.multiplier
            self.score += earned_points
            self.feedback_msg = (
                f"CORRECT! +{earned_points} "
                f"({self.multiplier}x) {self.num_a} {self.operator} {self.num_b} = {expected}"
            )
            self.feedback_color = (80, 230, 110)
            self.generate_new_card()
        else:
            self._reset_streak()
            self.feedback_msg = f"WRONG! Expected {expected}."
            self.feedback_color = (240, 75, 75)
            self.input_box.clear()

    def handle_timeout(self):
        """Count the current card as a failed attempt and advance to a new card."""
        if self.timed_out:
            return

        self.total_attempts += 1
        self._reset_streak()
        self.feedback_msg = "TIME'S UP!"
        self.feedback_color = (255, 165, 60)
        self.generate_new_card()

    def handle_event(self, event):
        # Handle the submit button before forwarding mouse input to the text
        # box. Otherwise clicking SUBMIT would deactivate the input box.
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_answer()
                return

        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_answer()

    def update(self):
        if self.timed_out:
            return

        elapsed = (pygame.time.get_ticks() - self.question_started_at) / 1000.0
        if elapsed >= self.QUESTION_TIME_LIMIT:
            self.handle_timeout()

    def get_time_remaining(self):
        """Return the current question's remaining time in seconds."""
        elapsed = (pygame.time.get_ticks() - self.question_started_at) / 1000.0
        return max(0.0, self.QUESTION_TIME_LIMIT - elapsed)

    def render(self, screen):
        screen.fill((25, 29, 37))

        title_surf = self.font_title.render("Math Flashcards Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 18))

        score_surf = self.font_hud.render(
            f"Score: {self.score} / {self.total_attempts}", True, (255, 220, 80)
        )
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 58))

        streak_surf = self.font_hud.render(
            f"Streak: {self.streak}   Multiplier: {self.multiplier}x",
            True,
            (180, 215, 255),
        )
        screen.blit(streak_surf, (self.width // 2 - streak_surf.get_width() // 2, 78))

        card_rect = pygame.Rect(self.width // 2 - 130, 105, 260, 100)
        pygame.draw.rect(screen, (240, 242, 245), card_rect, border_radius=12)
        pygame.draw.rect(screen, (85, 120, 175), card_rect, width=3, border_radius=12)

        card_str = f"{self.num_a}  {self.operator}  {self.num_b}"
        card_surf = self.font_card.render(card_str, True, (25, 30, 42))
        screen.blit(
            card_surf,
            (
                card_rect.centerx - card_surf.get_width() // 2,
                card_rect.centery - card_surf.get_height() // 2,
            ),
        )

        # Countdown timer bar below the card.
        timer_rect = pygame.Rect(self.width // 2 - 130, 212, 260, 10)
        remaining = self.get_time_remaining()
        fraction = remaining / self.QUESTION_TIME_LIMIT
        fill_width = int(timer_rect.width * fraction)
        pygame.draw.rect(screen, (65, 70, 80), timer_rect, border_radius=5)
        if fill_width > 0:
            pygame.draw.rect(
                screen,
                (75, 205, 105) if fraction > 0.5 else (240, 175, 40) if fraction > 0.2 else (240, 75, 75),
                pygame.Rect(timer_rect.x, timer_rect.y, fill_width, timer_rect.height),
                border_radius=5,
            )

        timer_surf = self.font_timer.render(f"Time: {remaining:0.1f}s", True, (210, 215, 225))
        screen.blit(timer_surf, (timer_rect.right - timer_surf.get_width(), timer_rect.bottom + 2))

        self.input_box.render(screen)

        pygame.draw.rect(screen, (45, 140, 80), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (215, 225, 220), self.submit_btn, width=2, border_radius=6)
        btn_txt = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(
            btn_txt,
            (
                self.submit_btn.centerx - btn_txt.get_width() // 2,
                self.submit_btn.centery - btn_txt.get_height() // 2,
            ),
        )

        msg_surf = self.font_hud.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(msg_surf, (self.width // 2 - msg_surf.get_width() // 2, 295))
