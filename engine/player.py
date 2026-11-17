"""The player. Shared by every room so the game feels the same on every floor."""
import math

import pygame

from . import config as C


class Keys:
    """What the player is pressing this frame. The game fills it from the keyboard; check.py fills it by script."""

    def __init__(self, left=False, right=False, up=False, down=False, jump=False):
        self.left, self.right, self.up, self.down, self.jump = left, right, up, down, jump


class Player:
    W, H = 22, 44

    def __init__(self, x, y_surface):
        self.x = float(x)
        self.y = float(y_surface - self.H)
        self.vx = self.vy = 0.0
        self.on = None          # the surface we stand on, or None in the air
        self.facing = 1
        self.spin = 0.0         # flip angle while airborne
        self.flipping = False
        self.walk = 0.0
        self.safe = 1.5         # seconds of no-harm after entering a room
        self.searching = None
        self._jump_was = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self, dt, keys, room):
        """Moves one step. Returns a list of events: 'piece', 'empty', 'dead', 'exit_left', 'exit_right'."""
        events = []
        self.safe = max(0.0, self.safe - dt)
        jump_pressed = keys.jump and not self._jump_was
        self._jump_was = keys.jump

        # Stand on a moving platform: it carries you.
        if self.on is not None and getattr(self.on, "carry", 0):
            self.x += self.on.carry

        # Ride a lift.
        if self.on is not None and hasattr(self.on, "drive") and (keys.up or keys.down):
            self.on.drive(-1 if keys.up else 1, dt)
            self.y = float(self.on.rect.top - self.H)   # snap to the lift's top so the landing test always holds
            self.vy = 0.0

        # Search furniture: stand still on the ground in front of it and hold UP.
        self.searching = None
        if self.on is not None and not hasattr(self.on, "drive") and keys.up:
            for f in room.furniture:
                if f.searched:
                    continue
                if f.rect.left <= self.rect.centerx <= f.rect.right and abs(f.rect.bottom - self.rect.bottom) <= 4:
                    self.searching = f
                    f.progress = min(1.0, f.progress + dt / C.SEARCH_SECONDS)
                    if f.progress >= 1.0:
                        f.searched = True
                        f.progress = 0.0
                        events.append("piece" if f.holds_piece else "empty")
                    break

        # Run (not while searching).
        self.vx = 0.0
        if self.searching is None:
            if keys.left and not keys.right:
                self.vx, self.facing = -C.RUN_SPEED, -1
            elif keys.right and not keys.left:
                self.vx, self.facing = C.RUN_SPEED, 1
        if self.on is not None and jump_pressed and self.searching is None:
            self.vy = -C.JUMP_SPEED
            self.on = None
            self.flipping = self.vx != 0.0
            self.spin = 0.0

        self.x += self.vx * dt
        self.walk = self.walk + abs(self.vx) * dt * 0.05 if self.on is not None else self.walk

        # Fall, and land on the highest surface we cross from above.
        prev_bottom = self.y + self.H
        self.vy = min(C.MAX_FALL, self.vy + C.GRAVITY * dt)
        self.y += self.vy * dt
        bottom = self.y + self.H
        self.on = None
        if self.vy >= 0:
            best = None
            for s in room.surfaces():
                r = s.rect
                if self.x + self.W > r.left and self.x < r.right and prev_bottom <= r.top + 1 and bottom >= r.top:
                    # highest surface wins; on a tie, stand on the lift so you can drive it
                    if best is None or r.top < best.rect.top or (r.top == best.rect.top and hasattr(s, "drive")):
                        best = s
            if best is not None:
                self.y = float(best.rect.top - self.H)
                self.vy = 0.0
                self.on = best
                self.flipping = False
                self.spin = 0.0
        if self.flipping:
            self.spin = (self.spin + 720 * dt * self.facing) % 360

        if self.y > C.H:            # fell out of the world: back to the floor
            self.y = float(C.FLOOR_Y - self.H)
            self.vy = 0.0
        if self.x + self.W < 0:
            events.append("exit_left")
        elif self.x > C.W:
            events.append("exit_right")

        if self.safe <= 0:
            me = self.rect
            for h in room.hazards:
                if me.colliderect(h.rect):
                    events.append("dead")
                    break
        return events

    def draw(self, surf):
        """An SVA student after hours: hoodie, jeans, white sneakers, a black portfolio case."""
        fig = pygame.Surface((self.W + 24, self.H + 10), pygame.SRCALPHA)
        cx, f = fig.get_width() // 2, self.facing
        skin, hoodie, trim, jeans, shoe, hair = (232, 192, 160), (44, 48, 60), (220, 60, 60), (52, 72, 110), (245, 245, 240), (36, 28, 24)
        if self.safe > 0 and int(self.safe * 10) % 2:
            hoodie = (120, 130, 160)
        airborne = self.on is None
        moving = (not airborne) and abs(self.vx) > 1
        s = math.sin(self.walk) if moving else 0.0
        hip, foot = 30, 44
        # legs: two segments each, knees bending on the stride; tucked up in the air
        for side in (-1, 1):
            if airborne:
                knee = (cx + side * 3 + 5 * f, hip + 6)
                toe = (cx + side * 3 - 2 * f, hip + 12)
            else:
                swing = 7 * s * side
                knee = (cx + side * 2 + swing * 0.6, hip + 7 - abs(swing) * 0.15)
                toe = (cx + side * 2 + swing, foot - max(0.0, -swing * side * 0.3))
            pygame.draw.line(fig, jeans, (cx + side * 2, hip), knee, 5)
            pygame.draw.line(fig, jeans, knee, toe, 5)
            pygame.draw.rect(fig, shoe, (toe[0] - 3 + 2 * f, toe[1] - 2, 7, 4), border_radius=2)
        # the portfolio case, held at the back hand
        case_x = cx - 13 * f - (5 if f > 0 else 0)
        sway = 2 * s
        pygame.draw.rect(fig, (18, 18, 22), (case_x, 18 + sway, 9, 16), border_radius=2)
        pygame.draw.line(fig, (120, 120, 130), (case_x + 2, 18 + sway), (case_x + 6, 18 + sway), 2)
        # hoodie: body, red drawstring trim, hood behind the head
        pygame.draw.rect(fig, hoodie, (cx - 8, 12, 16, 20), border_radius=5)
        pygame.draw.line(fig, trim, (cx - 7, 30), (cx + 7, 30), 2)
        pygame.draw.circle(fig, hoodie, (cx - 3 * f, 9), 6)
        # head, hair, an eye looking the way you face
        pygame.draw.circle(fig, skin, (cx + f, 7), 7)
        pygame.draw.arc(fig, hair, (cx + f - 7, 0, 14, 10), 0.2, 3.0, 4)
        pygame.draw.circle(fig, (20, 20, 24), (cx + 4 * f, 6), 1)
        # front arm: reaching while searching, up in a jump, swinging on the walk
        if self.searching is not None:
            hand = (cx + 11 * f, 12)
        elif airborne:
            hand = (cx + 7 * f, 6)
        else:
            hand = (cx + 6 * f - 6 * s * f, 29)
        pygame.draw.line(fig, hoodie, (cx + 2 * f, 16), hand, 4)
        pygame.draw.circle(fig, skin, hand, 2)
        if self.flipping:
            fig = pygame.transform.rotate(fig, -self.spin)
        r = fig.get_rect(center=(self.rect.centerx, self.rect.centery + 2))
        surf.blit(fig, r)
