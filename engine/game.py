"""The game loop's states: title, elevator, room, won, out of time. Floor authors don't edit this.

Two elevators. A floor's rooms run west to east: the first opens onto the WEST elevator at its left edge,
the last opens onto the EAST elevator at its right edge, and each room's right edge is the next room's
left edge. Rooms are keyed (floor, index), index 0 = westmost. The lobby is floor 1 (engine/lobby.py).
"""
import random

import pygame

from . import building, config as C, lobby, screens, sound
from .player import Keys, Player



class Game:
    def __init__(self, practice_floor=None, seed=None):
        pygame.font.init()
        self.big = pygame.font.Font(None, 64)
        self.mid = pygame.font.Font(None, 32)
        self.small = pygame.font.Font(None, 22)
        self.floors = building.load_floors(only=practice_floor)
        self.practice = practice_floor
        if practice_floor and practice_floor not in self.floors:
            raise SystemExit(f"no floor named {practice_floor!r} in floors/ (or it failed to import; run check.py)")
        self.where = building.place(self.floors)          # {floor number: file name}
        self.top = building.top(self.where)
        self.stops = {"west": building.west_stops(self.top), "east": building.east_stops(self.top)}
        self.rng = random.Random(seed)
        self.reset()

    # --- state ---------------------------------------------------------------------------------
    def reset(self):
        sound.ambient(True)        # the building at night, humming under everything
        self.rooms = {}            # {(floor number, index west to east): Room}
        self.count = {}            # {floor number: how many rooms}
        floors = [(1, [lobby.LEFT, lobby.RIGHT], lobby.AUTHOR)]
        floors += [(n, self.floors[f].room_classes, self.floors[f].author) for n, f in self.where.items()]
        for number, classes, author in floors:
            self.count[number] = len(classes)
            for i, cls in enumerate(classes):
                room = cls()
                room.author = author
                self.rooms[(number, i)] = room
        self.needed = max(1, min(building.PIECES_NEEDED, len(self.where)))
        self.digit = {n: self.rng.randrange(10) for n in self.where}   # each floor's digit of the door code
        self.code = []             # digits found, in the order found
        self.clock = float(C.CLOCK_SECONDS)
        self.toast, self.toast_t = "", 0.0
        self.shaft = "west"
        self.floor = 1.0
        self.moving = 0
        self.here = None           # (floor, index) of the room we're in
        self.player = None
        if self.practice:          # start on your own floor, walking in from the West elevator
            self.state = "room"
            self.enter((next(iter(self.where)), 0), "left")
        else:
            self.state = "title"
            self.enter((1, self.count[1] - 1), "left")        # at the security desk, its left side: security is between you and the East elevator
            self.state = "title"

    def toggle_light(self):
        """F: the flashlight on or off. It stays as you left it from room to room."""
        self.flashlight = not getattr(self, "flashlight", False)
        if self.player is not None:
            self.player.light_on = self.flashlight
        sound.play("click")

    def say(self, text, seconds=2.0):
        self.toast, self.toast_t = text, seconds

    def enter(self, door, edge):
        """Walk into the room at `door` through its `edge` ("left" or "right").

        Decision 6 (DECISIONS.md): coming in (or being sent back after you're caught) puts the room's lifts and robots
        back where they started. What's been searched stays searched. The room is rebuilt from its class
        and the searched marks are copied across, so this works for any floor without its author doing anything.
        """
        old = self.rooms[door]
        fresh = type(old)()
        fresh.author = old.author
        for a, b in zip(fresh.furniture, old.furniture):
            a.searched = b.searched
        self.rooms[door] = fresh
        self.here, self.came_in = door, edge
        x = C.W - 40 - Player.W if edge == "right" else 40
        self.player = Player(x, C.FLOOR_Y)
        self.player.facing = -1 if edge == "right" else 1
        self.player.light_on = getattr(self, "flashlight", False)
        self.state = "room"
        room = self.rooms[door]
        n = self.count[door[0]]
        where = f"  ({door[1] + 1} of {n})" if n > 2 else ""
        self.say(room.title if door[0] == 1 else f"{room.title}{where}  -  by {room.author}", 2.5)
        if room.dark > 0.5 and not getattr(self, "flashlight", False) and not getattr(self, "told_light", False):
            self.told_light = True                       # once a game: the first dark room
            self.say(f"Too dark? Press F for your flashlight   ({room.title})", 3.5)

    def board(self, shaft, floor):
        self.state = "elevator"
        self.shaft, self.floor, self.moving = shaft, float(floor), 0
        self.toast_t = 0.0
        self.player = None
        self.here = None

    # --- step ----------------------------------------------------------------------------------
    def step(self, dt, keys, pressed_start=False):
        self.toast_t = max(0.0, self.toast_t - dt)
        if self.state == "title":
            if pressed_start:
                self.state = "room"
                self.say("Security Desk  -  start here", 2.5)
            return
        if self.state in ("won", "lost"):
            if pressed_start:
                self.reset()
            return
        if not self.practice:
            self.clock -= dt
            if self.clock <= 0:
                self.clock = 0
                self.state = "lost"
                sound.play("lose")
                return
        if self.state == "elevator":
            self.step_elevator(dt, keys)
        elif self.state == "room":
            self.step_room(dt, keys)

    def step_elevator(self, dt, keys):
        speed = 3.0
        stops = self.stops[self.shaft]
        lo, hi = stops[0], stops[-1]
        if keys.up and self.floor < hi:
            self.moving = 1
        elif keys.down and self.floor > lo:
            self.moving = -1
        elif self.moving:          # keys let go: carry on to the next floor this elevator stops at
            # (a stop we're a hair short of still counts as ahead: floats drift, 2.9999999 is floor 3)
            ahead = [s for s in stops if (s >= self.floor - 1e-6 if self.moving > 0 else s <= self.floor + 1e-6)]
            target = (min(ahead) if self.moving > 0 else max(ahead)) if ahead else (hi if self.moving > 0 else lo)
            nxt = self.floor + self.moving * speed * dt
            if (self.moving > 0 and nxt >= target) or (self.moving < 0 and nxt <= target):
                self.floor, self.moving = float(target), 0
                sound.play("ding")
            else:
                self.floor = nxt
            return
        if self.moving:
            self.floor = max(float(lo), min(float(hi), self.floor + self.moving * speed * dt))
            return
        f = int(round(self.floor))
        out = keys.right if self.shaft == "west" else keys.left      # the floor is to the east of West
        if not out or f not in stops:
            return
        if f == building.GOAL:
            if len(self.code) >= self.needed:
                self.state = "won"
                sound.play("win")
            else:
                if self.toast_t <= 0:
                    sound.play("locked")
                self.say(f"MFA Computer Arts is locked: {len(self.code)} of {self.needed} code digits", 1.5)
        elif f in self.count:
            if self.shaft == "west":
                self.enter((f, 0), "left")
            else:
                self.enter((f, self.count[f] - 1), "right")

    def hear(self, room, p):
        """Robots make noise without knowing about sound: listen for what they do. A zapper switching on near you,
        a robot firing (mode "fire"), lunging (mode "lunge") or spotting you (alert) each make a sound."""
        heard = getattr(self, "_heard", {})
        now = {}
        for h in room.hazards:
            on, mode, alert = getattr(h, "on", None), getattr(h, "mode", None), getattr(h, "alert", None)
            was = heard.get(id(h), (on, mode, alert))
            near = hasattr(h, "rect") and abs(h.rect.centerx - p.rect.centerx) < 320
            if on and not was[0] and near:
                sound.play("zap")
            if mode != was[1] and mode == "fire":
                sound.play("zap")
            if mode != was[1] and mode == "lunge":
                sound.play("lunge")
            if alert and not was[2]:
                sound.play("alarm")
            now[id(h)] = (on, mode, alert)
        self._heard = now

    def step_room(self, dt, keys):
        door = self.here
        f, i = door
        last = self.count[f] - 1
        room, p = self.rooms[door], self.player
        room.tick(dt, p)
        self.hear(room, p)
        was_vy = p.vy
        events = p.update(dt, keys, room)
        if p.vy <= -C.JUMP_SPEED * 0.9 and was_vy > -C.JUMP_SPEED * 0.5:
            sound.play("jump")
        if "empty" in events:
            sound.play("nothing")
            self.say("Nothing here", 0.8)
        if "piece" in events and f in self.digit:
            sound.play("found")
            if self.practice:
                self.say(f"Code digit found: {self.digit[f]} (practice)")
            else:
                self.code.append(self.digit[f])
                self.say(f"Code digit: {self.digit[f]}   ({len(self.code)} of {self.needed})")
        if "dead" in events:
            sound.play("caught")
            if not self.practice:
                self.clock -= C.DEATH_PENALTY
            self.say(f"Caught! -{C.DEATH_PENALTY} seconds" if not self.practice else "Caught!")
            self.enter(door, self.came_in)      # back to the edge you came in by
            return
        if "exit_right" in events:
            if i < last:
                return self.enter((f, i + 1), "left")
            if f in self.stops["east"] and not self.practice:
                return self.board("east", f)
        if "exit_left" in events:
            if i > 0:
                return self.enter((f, i - 1), "right")
            if f in self.stops["west"] and not self.practice:
                return self.board("west", f)
        # no elevator at this end of this floor (or practice): that end wall is solid
        open_right = i < last or (f in self.stops["east"] and not self.practice)
        open_left = i > 0 or (f in self.stops["west"] and not self.practice)
        if not open_right and p.x > C.W - Player.W:
            p.x = float(C.W - Player.W)
            if self.practice:
                self.say("The East elevator is here (practice)", 0.8)
        if not open_left and p.x < 0:
            p.x = 0.0
            if self.practice:
                self.say("The West elevator is here (practice)", 0.8)

    # --- draw ----------------------------------------------------------------------------------
    def draw(self, surf):
        """The screens themselves are in engine/screens.py."""
        if self.state == "title":
            return screens.title(self, surf)
        if self.state == "elevator":
            screens.elevator(self, surf)
        elif self.state == "room":
            self.rooms[self.here].draw(surf, self.player)
        elif self.state == "won":
            return screens.end(self, surf, f"You made it to {building.FLOOR_NAMES[building.GOAL]}.", True)
        elif self.state == "lost":
            return screens.end(self, surf, "Out of time.", False)
        screens.hud(self, surf)

    def text(self, surf, s, font, color, center=None, topleft=None):
        img = font.render(s, True, color)
        r = img.get_rect()
        if center:
            r.center = center
        if topleft:
            r.topleft = topleft
        surf.blit(img, r)
        return r

    def digit_found(self, f):
        return any(x.holds_piece and x.searched for i in range(self.count[f]) for x in self.rooms[(f, i)].furniture)


def keys_from_keyboard():
    k = pygame.key.get_pressed()
    return Keys(left=k[pygame.K_LEFT] or k[pygame.K_a], right=k[pygame.K_RIGHT] or k[pygame.K_d],
                up=k[pygame.K_UP] or k[pygame.K_w], down=k[pygame.K_DOWN] or k[pygame.K_s],
                jump=k[pygame.K_SPACE])
