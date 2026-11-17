"""What's drawn around the rooms: the title, the elevator view, the HUD and the end screens.

Its owner is listed in OWNERS.md. These only draw; they don't change the game (that's engine/game.py), so
the owner can restyle every screen without touching a rule. `g` is the Game.
"""
import pygame

from . import building, config as C, lobby
from .player import Player

SPACING = 190          # screen pixels between floors in the elevator view
SHAFT_L, SHAFT_R = 410, 550


def title(g, surf):
    surf.fill(C.SHAFT)
    for i in range(12):
        y = 40 + i * 40
        pygame.draw.line(surf, (54, 58, 72), (0, y), (C.W, y), 1)
    g.text(surf, "TENTH FLOOR", g.big, C.PIECE, center=(C.W // 2, 150))
    g.text(surf, "SVA  /  West 21st Street  /  after hours", g.small, (200, 204, 214), center=(C.W // 2, 196))
    g.text(surf, f"Get into floor {building.GOAL}, MFA Computer Arts, before the clock runs out.", g.mid,
              C.HUD, center=(C.W // 2, 230))
    g.text(surf, f"Its door takes a {g.needed}-digit code. Every floor hides one digit.", g.mid, C.HUD,
              center=(C.W // 2, 266))
    lines = ["arrows: move  /  SPACE: jump (run + jump to flip)  /  hold UP at furniture: search",
             "UP or DOWN on a yellow lift or in an elevator: ride  /  walk across a floor to switch elevators",
             "press SPACE to start"]
    for i, s in enumerate(lines):
        g.text(surf, s, g.small, (200, 204, 214), center=(C.W // 2, 350 + i * 28))


def elevator(g, surf):
    """One shaft, seen side on: the floor's door is to the right of West, to the left of East."""
    surf.fill((34, 36, 46))
    cy = C.H // 2 + 70
    stops = g.stops[g.shaft]
    for f in range(min(1, g.stops["west"][0]), g.top + 1):
        y = int(cy - (f - g.floor) * SPACING)
        if y < -SPACING or y > C.H + SPACING:
            continue
        stop = f in stops
        pygame.draw.rect(surf, (52, 56, 70) if stop else (40, 42, 52), (0, y - SPACING + 8, C.W, SPACING - 8))
        pygame.draw.rect(surf, (90, 92, 100), (0, y, C.W, 10))
        dx = SHAFT_R + 20 if g.shaft == "west" else SHAFT_L - 90
        door = pygame.Rect(dx, y - 90, 70, 90)
        num_x = door.right + 40 if g.shaft == "west" else door.left - 40
        g.text(surf, building.label(f), g.big, (90, 96, 116) if stop else (60, 64, 76), center=(num_x, y - 45))
        if not stop:
            label = "(this elevator doesn't stop here)"
            pygame.draw.rect(surf, (48, 50, 58), door)
        elif f == building.GOAL:
            open_ = len(g.code) >= g.needed
            pygame.draw.rect(surf, (90, 160, 90) if open_ else (120, 60, 60), door)
            label = "MFA Computer Arts: " + ("OPEN" if open_ else f"LOCKED  {len(g.code)}/{g.needed}")
        elif f in g.count:
            pygame.draw.rect(surf, (150, 120, 80), door)
            if f in g.digit and g.digit_found(f):
                pygame.draw.circle(surf, C.PIECE, door.center, 12)
                g.text(surf, str(g.digit[f]), g.small, C.INK, center=door.center)
            label = lobby.NAME if f == 1 else g.floors[g.where[f]].name
        else:
            pygame.draw.rect(surf, (60, 62, 70), door)
            label = "(no floor yet)"
        pygame.draw.rect(surf, C.INK, door, 2)
        img = g.small.render(label, True, (220, 220, 228))
        r = img.get_rect()
        r.bottom = door.top - 6
        if g.shaft == "west":
            r.left = door.left
        else:
            r.right = door.right
        surf.blit(img, r)
    pygame.draw.rect(surf, C.SHAFT, (SHAFT_L, 0, SHAFT_R - SHAFT_L, C.H))
    for x in (SHAFT_L + 20, SHAFT_R - 20):
        pygame.draw.line(surf, (24, 26, 32), (x, 0), (x, C.H), 3)
    car = pygame.Rect(SHAFT_L + 10, cy - 100, SHAFT_R - SHAFT_L - 20, 100)
    pygame.draw.rect(surf, (120, 124, 136), car)
    pygame.draw.rect(surf, C.INK, car, 3)
    figure = Player(car.centerx - Player.W // 2, car.bottom - 4)
    figure.safe = 0
    figure.draw(surf)
    f = int(round(g.floor))
    name = lobby.NAME if f == 1 else building.floor_name(f, g.where, g.floors)
    if f in g.where:
        name += f"  -  {g.floors[g.where[f]].author}"
    panel = pygame.Rect(0, 34, C.W, 62)
    pygame.draw.rect(surf, (24, 26, 34), panel)
    out = "RIGHT" if g.shaft == "west" else "LEFT"
    g.text(surf, f"{g.shaft.upper()} ELEVATOR  -  floor {building.label(f)}  -  UP / DOWN to ride, {out} to step out",
              g.small, (170, 176, 190), center=(C.W // 2, 50))
    g.text(surf, name, g.mid, C.HUD, center=(C.W // 2, 76))


def hud(g, surf):
    bar = pygame.Surface((C.W, 34), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 150))
    surf.blit(bar, (0, 0))
    if g.practice:
        g.text(surf, f"PRACTICE: {g.practice}  (no clock; Esc quits)", g.mid, C.HUD, topleft=(12, 6))
    else:
        m, s = divmod(int(g.clock), 60)
        g.text(surf, f"{m:02d}:{s:02d}", g.mid, C.DANGER if g.clock < 60 else C.HUD, topleft=(12, 6))
        g.text(surf, "CODE", g.small, (200, 200, 200), topleft=(96, 11))
        for i in range(g.needed):
            box = pygame.Rect(146 + i * 24, 7, 20, 22)
            if i < len(g.code):
                pygame.draw.rect(surf, C.PIECE, box, border_radius=3)
                g.text(surf, str(g.code[i]), g.mid, C.INK, center=box.center)
            else:
                pygame.draw.rect(surf, (90, 90, 90), box, 2, border_radius=3)
    if g.toast_t > 0:
        y = C.FLOOR_Y + (C.H - C.FLOOR_Y) // 2      # on the floor strip, clear of every room's art
        g.text(surf, g.toast, g.mid, C.PIECE, center=(C.W // 2, y))


def _owners():
    """Claimed pieces from OWNERS.md: [(piece, owner)], skipping open ones and the maintainer's."""
    import os
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "OWNERS.md")
    out = []
    try:
        for line in open(path, encoding="utf-8"):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) >= 5 and cells[1] and cells[1] != "piece" and not set(cells[1]) <= set("-"):
                owner = cells[2]
                if owner and owner.lower() != "open" and "maintainer" not in owner:
                    out.append((cells[1].split(":")[0], owner))
    except OSError:
        pass
    return out


def end(g, surf, line, won):
    surf.fill((20, 40, 24) if won else (46, 20, 20))
    g.text(surf, line, g.big, C.PIECE if won else C.DANGER, center=(C.W // 2, 70))
    if won:
        m, s = divmod(int(g.clock), 60)
        g.text(surf, f"code {' '.join(map(str, g.code))}  -  with {m:02d}:{s:02d} left", g.mid, C.HUD,
               center=(C.W // 2, 118))
        # the credits roll: every floor, bottom to top, then every piece with an owner
        if getattr(g, "_won_at", None) is None:
            g._won_at = pygame.time.get_ticks()
        rows = [("THE BUILDING", None)]
        floors = {1: ("Lobby / Flatiron Gallery", "the class"), building.GOAL: ("MFA Computer Arts", "you got in")}
        floors.update({n: (g.floors[f].name, g.floors[f].author) for n, f in g.where.items()})
        rows += [(f"{building.label(n)}  {name}", who) for n, (name, who) in sorted(floors.items())]
        owned = _owners()
        if owned:
            rows += [("", None), ("THE PIECES", None)] + owned
        rows += [("", None), ("Programming for Animators  -  Fall 2026", None)]
        clip = pygame.Rect(0, 150, C.W, C.H - 190)
        span = len(rows) * 30 + clip.height                    # once it has all gone by, it starts again
        y = clip.bottom - ((pygame.time.get_ticks() - g._won_at) / 1000 * 40) % span
        surf.set_clip(clip)
        for i, (left, right) in enumerate(rows):
            ry = int(y + i * 30)
            if right is None:
                g.text(surf, left, g.mid, C.PIECE, center=(C.W // 2, ry))
            else:
                img_l = g.small.render(left, True, C.HUD)
                img_r = g.small.render(right, True, (190, 200, 190))
                surf.blit(img_l, img_l.get_rect(midright=(C.W // 2 - 14, ry)))
                surf.blit(img_r, img_r.get_rect(midleft=(C.W // 2 + 14, ry)))
        surf.set_clip(None)
    else:
        g._won_at = None
        authors = sorted({fl.author for fl in g.floors.values()})
        g.text(surf, "Floors by", g.mid, (200, 200, 200), center=(C.W // 2, 250))
        for i, a in enumerate(authors):
            g.text(surf, a, g.small, C.HUD, center=(C.W // 2, 284 + i * 22))
    g.text(surf, "SPACE to play again", g.small, (200, 200, 200), center=(C.W // 2, C.H - 24))
