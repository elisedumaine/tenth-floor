"""Kit part: SecurityTerminal (furniture + its control). Its owner is listed in OWNERS.md."""
import pygame

from .. import config as C
from ._base import INK, KitFurniture

__all__ = ["SecurityTerminal"]


class _Control:
    """The terminal's wiring, kept in self.hazards so the room updates it every frame. It never hurts anyone."""

    def __init__(self, terminal):
        self.terminal = terminal
        self.rect = pygame.Rect(0, 0, 0, 0)       # nothing to touch
        self.frozen = 0.0
        self.cooldown = 0.0
        self.held = []

    def update(self, dt, room, player):
        t = self.terminal
        if self.frozen > 0:
            self.frozen -= dt
            player.safe = max(player.safe, self.frozen)            # robots can't hurt you while they're down
            if self.frozen <= 0:
                for h in self.held:                                  # wake them up
                    h.__dict__.pop("update", None)
                self.held, self.cooldown = [], t.COOLDOWN
        elif self.cooldown > 0:
            self.cooldown -= dt
            if self.cooldown <= 0:
                t.searched = False                                   # ready to use again
        elif t.searched:
            self.frozen = t.FREEZE
            self.held = [h for h in room.hazards if h is not self]
            for h in self.held:                                      # each robot skips its own update: it stands still
                h.update = lambda *a, **k: None
        t.frozen, t.cooling = max(0.0, self.frozen), self.cooldown > 0

    def draw(self, surf):
        pass


class SecurityTerminal(KitFurniture):
    """A security terminal on a desk. Search it and every robot and hazard in this room freezes for FREEZE
    seconds, and none of them can hurt you. After COOLDOWN seconds it can be used again.

    It needs two lines in build():
        terminal = SecurityTerminal(300, C.FLOOR_Y)
        self.furniture.append(terminal); self.hazards.append(terminal.control)
    It never holds your floor's digit.
    """

    W, H, NAME = 72, 64, "security terminal"
    FREEZE, COOLDOWN = 5.0, 6.0

    def __init__(self, x, y, name=None):
        super().__init__(x, y, name)
        self.control = _Control(self)
        self.frozen, self.cooling = 0.0, False
        self.font = pygame.font.Font(None, 16)

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, (80, 84, 96), (r.left, r.top + 30, r.width, r.height - 30))     # the desk
        pygame.draw.rect(surf, INK, (r.left, r.top + 30, r.width, r.height - 30), 2)
        screen = pygame.Rect(r.left + 6, r.top, r.width - 12, 28)
        if self.frozen > 0:
            col, text = (60, 160, 90), f"OFF {self.frozen:.0f}"
        elif self.cooling:
            col, text = (120, 110, 60), "REBOOT"
        else:
            col, text = (40, 70, 120), "SECURITY"
        pygame.draw.rect(surf, col, screen)
        pygame.draw.rect(surf, INK, screen, 2)
        img = self.font.render(text, True, (235, 240, 245))
        surf.blit(img, img.get_rect(center=screen.center))
