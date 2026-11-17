"""Kit part: Sentry (hazard). Its owner is listed in OWNERS.md."""
import pygame

from .. import config as C
from ._base import INK

__all__ = ["Sentry"]


class Sentry:
    """A guard robot that stands at its post and turns to face you.

    It stays at x until you're on its level and in front of it, within `sight` px. Hold its gaze for `wind_up`
    seconds and it lunges at you fast, as far as left..right, then rolls back to its post. Jump it as it comes,
    or keep off its level. Behind it is no hiding place: it turns around.
    """

    W, H = 34, 46

    def __init__(self, x, y, left, right, sight=260, wind_up=0.6, lunge=280.0, back=70.0):
        self.post, self.x, self.y_surface = float(x), float(x), int(y)
        self.left, self.right = int(left), int(right)
        self.sight, self.wind_up, self.lunge, self.back = int(sight), wind_up, float(lunge), float(back)
        self.dir = -1
        self.mode, self.timer = "watch", 0.0      # watch -> lunge -> return -> watch
        self.rect = pygame.Rect(int(x), self.y_surface - self.H, self.W, self.H)

    def update(self, dt, room, player):
        level = abs(player.rect.bottom - self.y_surface) < 6
        dx = player.rect.centerx - self.rect.centerx
        if self.mode == "watch":
            if level and dx:
                self.dir = 1 if dx > 0 else -1                       # it turns to face you
            if level and abs(dx) < self.sight:
                self.timer += dt
                if self.timer >= self.wind_up:
                    self.mode, self.timer = "lunge", 0.0
            else:
                self.timer = max(0.0, self.timer - dt)
        elif self.mode == "lunge":
            self.x += self.dir * self.lunge * dt
            self.timer += dt
            if self.timer > 0.8 or self.x < self.left or self.x + self.W > self.right:
                self.x = max(float(self.left), min(float(self.right - self.W), self.x))
                self.mode = "return"
        elif self.mode == "return":
            step = self.back * dt
            if abs(self.post - self.x) <= step:
                self.x, self.mode, self.timer = self.post, "watch", 0.0
            else:
                self.x += step if self.post > self.x else -step
        self.rect.x = int(self.x)

    def draw(self, surf):
        r = self.rect
        tense = self.mode == "watch" and self.timer > 0
        pygame.draw.rect(surf, (96, 70, 70) if self.mode == "lunge" else (70, 72, 86), r, border_radius=5)
        pygame.draw.rect(surf, INK, r, 2, border_radius=5)
        visor = pygame.Rect(r.left + 4, r.top + 8, r.width - 8, 10)
        pygame.draw.rect(surf, (20, 22, 28), visor)
        eye_x = r.centerx + self.dir * 8
        pygame.draw.circle(surf, C.DANGER if tense or self.mode == "lunge" else (150, 230, 255), (eye_x, visor.centery), 4)
        if tense:                                                    # it's about to come for you
            pygame.draw.line(surf, C.DANGER, (r.centerx, r.top - 12), (r.centerx, r.top - 4), 3)
            pygame.draw.circle(surf, C.DANGER, (r.centerx, r.top - 1), 2)
        pygame.draw.rect(surf, INK, (r.left + 4, r.bottom - 6, r.width - 8, 6))
