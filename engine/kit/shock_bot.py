"""Kit part: ShockBot (hazard). Its owner is listed in OWNERS.md."""
import math
import random

import pygame

from .. import config as C
from ._base import INK

__all__ = ["ShockBot"]


class ShockBot:
    """A security robot that shoots an electric bolt along the floor.

    It patrols between left and right on the surface y (C.FLOOR_Y, or a ledge's y). When you're on its level
    and in front of it, within `sight` px, it rolls toward you; once you're within reach it stops, charges up (it flickers and sparks: that's your warning),
    then fires a bolt `reach` px long in front of it. Jump the bolt, or stay off its level. After a shot it
    rests for `rest` seconds before it can charge again.
    """

    W, H = 36, 42
    BOLT_H = 14          # the bolt runs at knee height; a jump clears it

    def __init__(self, x, y, left, right, speed=60.0, sight=320, reach=240, charge=0.7, fire=0.35, rest=1.6):
        self.x, self.y_surface = float(x), int(y)
        self.left, self.right, self.speed = int(left), int(right), float(speed)
        self.sight, self.reach = int(sight), int(reach)
        self.charge_time, self.fire_time, self.rest_time = charge, fire, rest
        self.dir = 1
        self.mode, self.timer = "patrol", 0.0       # patrol -> charge -> fire -> rest -> patrol
        self.body = pygame.Rect(int(self.x), self.y_surface - self.H, self.W, self.H)
        self.rect = self.body.copy()
        self.t = 0.0

    def bolt_rect(self):
        y = self.y_surface - 24
        if self.dir > 0:
            return pygame.Rect(self.body.right, y, self.reach, self.BOLT_H)
        return pygame.Rect(self.body.left - self.reach, y, self.reach, self.BOLT_H)

    def update(self, dt, room, player):
        self.t += dt
        self.timer -= dt
        level = abs(player.rect.bottom - self.y_surface) < 6
        gap = (player.rect.centerx - self.body.centerx) * self.dir
        sees = level and 0 < gap < self.sight
        if self.mode == "patrol":
            if sees and gap < self.reach - 30:
                self.mode, self.timer = "charge", self.charge_time
            else:
                self.x += self.dir * self.speed * (1.8 if sees else 1.0) * dt     # closes in once it sees you
                if self.x < self.left:
                    self.x, self.dir = float(self.left), 1
                elif self.x + self.W > self.right:
                    self.x, self.dir = float(self.right - self.W), -1
        elif self.mode == "charge" and self.timer <= 0:
            self.mode, self.timer = "fire", self.fire_time
        elif self.mode == "fire" and self.timer <= 0:
            self.mode, self.timer = "rest", self.rest_time
        elif self.mode == "rest" and self.timer <= 0:
            self.mode = "patrol"
        self.body.x = int(self.x)
        # While it fires, its reach is part of what hits you: the box grows to cover the bolt.
        self.rect = self.body.union(self.bolt_rect()) if self.mode == "fire" else self.body.copy()

    def draw(self, surf):
        r = self.body
        charging = self.mode == "charge"
        flick = charging and int(self.t * 16) % 2 == 0
        pygame.draw.rect(surf, (230, 210, 80) if flick else (70, 74, 90), r, border_radius=6)
        pygame.draw.rect(surf, INK, r, 2, border_radius=6)
        # the coil on its head
        for i in range(3):
            pygame.draw.circle(surf, (190, 200, 220), (r.centerx, r.top - 4 - i * 5), 4 - i, 1)
        eye_x = r.centerx + self.dir * 9
        pygame.draw.circle(surf, C.DANGER if self.mode in ("charge", "fire") else (120, 220, 255), (eye_x, r.top + 14), 6)
        pygame.draw.circle(surf, INK, (r.left + 9, r.bottom), 5)
        pygame.draw.circle(surf, INK, (r.right - 9, r.bottom), 5)
        if charging:                                  # sparks around the coil: the warning
            rnd = random.Random(int(self.t * 20))
            for _ in range(4):
                a = rnd.uniform(0, 2 * math.pi)
                x0, y0 = r.centerx, r.top - 10
                pygame.draw.line(surf, (255, 240, 140), (x0, y0),
                                 (x0 + int(14 * math.cos(a)), y0 + int(14 * math.sin(a))), 2)
        if self.mode == "fire":                       # the bolt: a jagged line along the floor
            b = self.bolt_rect()
            rnd = random.Random(int(self.t * 30))
            xs = range(b.left, b.right + 1, 16)
            pts = [(x, b.centery + rnd.randint(-6, 6)) for x in xs]
            if len(pts) > 1:
                pygame.draw.lines(surf, (120, 200, 255), False, pts, 5)
                pygame.draw.lines(surf, (240, 250, 255), False, pts, 2)
