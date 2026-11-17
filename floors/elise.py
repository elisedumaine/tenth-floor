"""Art History Center, 4th floor: the reading room, the slide and archive room, then the lecture room.

West elevator -> Reading Room -> Slide and Archive Room -> Lecture Room -> East elevator.
The digit is in the archive box up on the top shelf of the Slide and Archive Room: ride the lift up to it,
and watch the crusher (the archive's book press).
"""
import pygame

from engine import config as C
from engine.kit import (Bookshelf, CeilingLight, Crusher, Desk, Drone, FilingCabinet, FloorLaser, PatrolBot,
                        Plant, Poster, Sign, Window)
from engine.room import Furniture, Lift, Platform, Room

NAME = "Art History Center"     # the name on the elevator panel
AUTHOR = "Elise Dumaine"        # your name


# --- my own parts ---

class Painting:
    """Decor: a framed painting on the wall. style picks which one."""

    def __init__(self, x, y, w, h, style="mondrian"):
        self.pos = (x, y)
        self.image = pygame.Surface((w, h))          # painted once, not every frame
        draw_artwork(self.image, style)
        pygame.draw.rect(self.image, (176, 140, 60), self.image.get_rect(), 6)   # gold frame
        pygame.draw.rect(self.image, C.INK, self.image.get_rect(), 2)

    def draw(self, surf):
        surf.blit(self.image, self.pos)


def draw_artwork(img, style):
    w, h = img.get_size()
    if style == "mondrian":
        img.fill((240, 236, 224))
        pygame.draw.rect(img, (200, 40, 40), (0, 0, w * 0.55, h * 0.6))
        pygame.draw.rect(img, (30, 60, 150), (0, h * 0.75, w * 0.3, h))
        pygame.draw.rect(img, (240, 200, 40), (w * 0.8, h * 0.75, w, h))
        for x in (w * 0.3, w * 0.55, w * 0.8):
            pygame.draw.line(img, C.INK, (x, 0), (x, h), 5)
        for y in (h * 0.6, h * 0.75):
            pygame.draw.line(img, C.INK, (0, y), (w, y), 5)
    elif style == "night":                         # a starry night
        img.fill((30, 50, 110))
        for i in range(6):
            pygame.draw.arc(img, (90, 130, 200), (i * w // 5 - 20, h // 5, w // 3, h // 3), 0, 3.1, 3)
        pygame.draw.circle(img, (250, 220, 90), (int(w * 0.8), int(h * 0.22)), max(6, w // 10))
        for sx, sy in ((0.2, 0.15), (0.45, 0.1), (0.6, 0.3), (0.3, 0.4)):
            pygame.draw.circle(img, (250, 240, 150), (int(w * sx), int(h * sy)), 4)
        pygame.draw.polygon(img, (20, 40, 30), [(w * 0.15, h), (w * 0.22, h * 0.3), (w * 0.3, h)])
        pygame.draw.rect(img, (40, 60, 70), (0, h * 0.8, w, h))
    elif style == "mona lisa":                      # Leonardo: hazy landscape, dark dress, folded hands
        img.fill((110, 120, 80))
        pygame.draw.rect(img, (140, 150, 110), (0, 0, w, h * 0.35))
        pygame.draw.polygon(img, (90, 100, 70), [(0, h * 0.45), (w * 0.3, h * 0.3), (w, h * 0.4), (w, h), (0, h)])
        pygame.draw.ellipse(img, (40, 34, 24), (w * 0.12, h * 0.55, w * 0.76, h * 0.7))      # dress
        pygame.draw.ellipse(img, (40, 30, 20), (w * 0.27, h * 0.1, w * 0.46, h * 0.55))      # hair
        pygame.draw.ellipse(img, (210, 170, 110), (w * 0.35, h * 0.14, w * 0.3, h * 0.4))    # face
        pygame.draw.polygon(img, (210, 170, 110), [(w * 0.38, h * 0.56), (w * 0.62, h * 0.56), (w * 0.5, h * 0.66)])
        pygame.draw.arc(img, (120, 70, 50), (w * 0.43, h * 0.38, w * 0.14, h * 0.05), 3.4, 6.0, 2)  # the smile
        for ex in (0.44, 0.56):
            pygame.draw.circle(img, (60, 40, 30), (int(w * ex), int(h * 0.3)), 2)
        pygame.draw.ellipse(img, (210, 170, 110), (w * 0.35, h * 0.8, w * 0.32, h * 0.1))     # hands
    elif style == "pearl":                          # Vermeer: blue and yellow turban, the pearl
        img.fill((22, 20, 22))
        pygame.draw.ellipse(img, (100, 80, 60), (w * 0.2, h * 0.7, w * 0.7, h * 0.5))         # jacket
        pygame.draw.ellipse(img, (230, 200, 160), (w * 0.3, h * 0.25, w * 0.42, h * 0.5))     # face
        pygame.draw.ellipse(img, (40, 80, 170), (w * 0.22, h * 0.1, w * 0.48, h * 0.3))       # turban
        pygame.draw.polygon(img, (220, 190, 90), [(w * 0.55, h * 0.18), (w * 0.8, h * 0.25), (w * 0.72, h * 0.6),
                                                  (w * 0.62, h * 0.3)])
        pygame.draw.circle(img, (60, 40, 30), (int(w * 0.45), int(h * 0.45)), 3)
        pygame.draw.circle(img, (60, 40, 30), (int(w * 0.6), int(h * 0.44)), 2)
        pygame.draw.circle(img, (180, 60, 60), (int(w * 0.5), int(h * 0.64)), 3)               # lips
        pygame.draw.circle(img, (245, 245, 240), (int(w * 0.36), int(h * 0.66)), 4)            # the pearl
    elif style == "scream":                         # Munch: orange sky, blue fjord, the screaming figure
        img.fill((220, 110, 50))
        for i, y in enumerate(range(0, int(h * 0.5), 10)):
            pygame.draw.arc(img, ((240, 160, 60), (200, 70, 40))[i % 2], (-20, y, w + 40, 24), 0, 3.1, 4)
        pygame.draw.ellipse(img, (40, 70, 120), (-w * 0.2, h * 0.4, w * 0.9, h * 0.3))         # fjord
        pygame.draw.polygon(img, (130, 90, 60), [(0, h), (w * 0.2, h), (w, h * 0.45), (w, h * 0.55)])   # bridge
        pygame.draw.line(img, (90, 60, 40), (0, h * 0.85), (w, h * 0.38), 3)                  # rail
        pygame.draw.ellipse(img, (50, 50, 60), (w * 0.32, h * 0.62, w * 0.3, h * 0.45))       # body
        pygame.draw.ellipse(img, (220, 200, 150), (w * 0.36, h * 0.42, w * 0.22, h * 0.26))   # head
        pygame.draw.ellipse(img, (40, 30, 30), (w * 0.44, h * 0.56, w * 0.06, h * 0.08))      # mouth
        for ex in (0.42, 0.52):
            pygame.draw.circle(img, (40, 30, 30), (int(w * ex), int(h * 0.5)), 2)
        for hx in (0.33, 0.58):
            pygame.draw.ellipse(img, (220, 200, 150), (w * hx, h * 0.48, w * 0.06, h * 0.16))  # hands on cheeks


class ProjectorScreen:
    """Decor: the pull-down screen in the lecture room, showing today's slide."""

    def __init__(self, x, y, w, h):
        self.pos = (x, y)
        self.image = pygame.Surface((w, h + 14))
        self.image.fill((70, 74, 88))
        pygame.draw.rect(self.image, (60, 60, 66), (0, 0, w, 10))                 # the roller
        pygame.draw.rect(self.image, (238, 238, 232), (4, 10, w - 8, h))
        slide = pygame.Surface((int(w * 0.6), int(h * 0.75)))
        draw_artwork(slide, "mondrian")
        self.image.blit(slide, (w // 2 - slide.get_width() // 2, 10 + h // 2 - slide.get_height() // 2))
        self.image.set_colorkey((70, 74, 88))

    def draw(self, surf):
        surf.blit(self.image, self.pos)


class LightTable(Furniture):
    """A glowing table covered in 35 mm slides."""

    def __init__(self, x, y, name="light table", holds_piece=False, w=120, h=40):
        super().__init__(x, y, w, h, name, holds_piece)

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, (90, 84, 76), (r.left + 8, r.top + 10, 6, r.height - 10))
        pygame.draw.rect(surf, (90, 84, 76), (r.right - 14, r.top + 10, 6, r.height - 10))
        top = pygame.Rect(r.left, r.top, r.width, 12)
        pygame.draw.rect(surf, (250, 246, 220) if not self.searched else (170, 168, 156), top)
        pygame.draw.rect(surf, C.INK, top, 2)
        for i, x in enumerate(range(r.left + 8, r.right - 14, 18)):
            color = ((200, 80, 60), (60, 110, 180), (220, 190, 60), (90, 150, 90))[i % 4]
            pygame.draw.rect(surf, color, (x, r.top + 3, 12, 7))


class ArchiveBox(Furniture):
    """A stack of labeled archive boxes."""

    def __init__(self, x, y, name="archive boxes", holds_piece=False, w=70, h=60):
        super().__init__(x, y, w, h, name, holds_piece)

    def draw(self, surf):
        r = self.rect
        body = (196, 170, 120) if not self.searched else (140, 130, 112)
        half = r.height // 2
        for i, box in enumerate((pygame.Rect(r.left, r.top + half, r.width, half),
                                 pygame.Rect(r.left + 6, r.top, r.width - 12, half))):
            pygame.draw.rect(surf, body, box)
            pygame.draw.rect(surf, C.INK, box, 2)
            pygame.draw.rect(surf, (240, 236, 224), (box.centerx - 12, box.top + 8, 24, 10))


class Lectern(Furniture):
    """The professor's lectern."""

    def __init__(self, x, y, name="lectern", holds_piece=False, w=50, h=90):
        super().__init__(x, y, w, h, name, holds_piece)

    def draw(self, surf):
        r = self.rect
        wood = (120, 80, 50) if not self.searched else (100, 90, 80)
        pygame.draw.rect(surf, wood, (r.left + 8, r.top + 16, r.width - 16, r.height - 16))
        pygame.draw.polygon(surf, wood, [(r.left, r.top + 18), (r.right, r.top + 18), (r.right - 4, r.top),
                                         (r.left + 4, r.top)])
        pygame.draw.rect(surf, C.INK, (r.left + 8, r.top + 16, r.width - 16, r.height - 16), 2)
        pygame.draw.polygon(surf, C.INK, [(r.left, r.top + 18), (r.right, r.top + 18), (r.right - 4, r.top),
                                          (r.left + 4, r.top)], 2)


class Seats(Furniture):
    """A row of folding lecture seats."""

    def __init__(self, x, y, name="seats", holds_piece=False, w=100, h=34):
        super().__init__(x, y, w, h, name, holds_piece)

    def draw(self, surf):
        r = self.rect
        red = (150, 50, 50) if not self.searched else (110, 90, 90)
        for x in range(r.left, r.right - 20, 34):
            pygame.draw.rect(surf, red, (x, r.top, 28, r.height - 14), border_radius=4)
            pygame.draw.rect(surf, red, (x, r.bottom - 16, 30, 8), border_radius=2)
            pygame.draw.line(surf, C.INK, (x + 14, r.bottom - 8), (x + 14, r.bottom), 3)
            pygame.draw.rect(surf, C.INK, (x, r.top, 28, r.height - 14), 2, border_radius=4)


# --- the rooms, west to east ---

class ReadingRoom(Room):
    title = "Reading Room"

    def build(self):
        self.decor += [Sign(370, 46, "READING ROOM", (230, 200, 140)), CeilingLight(250), CeilingLight(700),
                       Window(640, 80, seed=4), Painting(120, 90, 90, 130, "mona lisa"),
                       Painting(240, 110, 110, 80, "night"), Painting(470, 110, 80, 100, "pearl")]
        self.platforms.append(Platform(380, 400, 200))
        self.furniture += [Bookshelf(130, C.FLOOR_Y), Bookshelf(420, 400), Desk(640, C.FLOOR_Y, "study desk"),
                           Plant(800, C.FLOOR_Y)]
        self.hazards.append(PatrolBot(300, C.FLOOR_Y, left=200, right=780, speed=70))

    def draw_background(self, surf):
        surf.fill((92, 72, 60))                                   # warm wood paneling
        pygame.draw.rect(surf, (74, 56, 46), (0, 360, C.W, C.FLOOR_Y - 360))
        for x in range(0, C.W, 120):
            pygame.draw.line(surf, (70, 54, 44), (x, 360), (x, C.FLOOR_Y), 2)


class SlideArchive(Room):
    """The digit is in the archive boxes on the top shelf: take the lift up, then dodge the book press."""

    title = "Slide and Archive Room"

    def build(self):
        self.decor += [Sign(330, 46, "SLIDE AND ARCHIVE ROOM", (200, 220, 240)), CeilingLight(470),
                       Poster(150, 90, "35mm", (70, 110, 160)), Poster(240, 90, "ARCHIVE", (150, 110, 70), w=96)]
        self.platforms.append(Platform(150, 400, 180))
        self.platforms.append(Platform(360, 300, 180))
        self.platforms.append(Platform(630, 200, 240))
        self.lifts.append(Lift(560, y_top=200, y_bottom=C.FLOOR_Y, width=64))
        self.furniture += [FilingCabinet(180, 400, "slide drawers"), LightTable(380, 300),
                           ArchiveBox(650, 200, holds_piece=True), FilingCabinet(800, 200, "old catalogs"),
                           Desk(660, C.FLOOR_Y, "scanner desk")]
        self.hazards.append(FloorLaser(200, 520, on_time=1.2, off_time=1.6))
        self.hazards.append(Crusher(735, y_top=80, y_bottom=200, w=50, h=40))

    def draw_background(self, surf):
        surf.fill((50, 56, 70))                                   # dim, cool storage room
        for y in range(80, C.FLOOR_Y, 70):
            pygame.draw.line(surf, (60, 66, 82), (0, y), (C.W, y), 2)


class LectureRoom(Room):
    title = "Lecture Room"

    def build(self):
        self.decor += [Sign(380, 46, "LECTURE ROOM", (240, 220, 180)), ProjectorScreen(120, 90, 260, 170),
                       Poster(430, 100, "ART HIST", (130, 60, 70), w=96), Painting(545, 110, 80, 110, "scream"), CeilingLight(620), CeilingLight(820)]
        self.platforms.append(Platform(560, 440, 140))      # the tiered seats
        self.platforms.append(Platform(690, 380, 140))
        self.furniture += [Plant(100, C.FLOOR_Y), Lectern(300, C.FLOOR_Y), Seats(575, 440), Seats(710, 380)]
        self.hazards.append(Drone(450, y_top=300, y_bottom=C.FLOOR_Y, speed=80))
        self.hazards.append(PatrolBot(700, C.FLOOR_Y, left=540, right=850, speed=60))

    def draw_background(self, surf):
        surf.fill((64, 60, 74))
        pygame.draw.rect(surf, (54, 50, 62), (0, 300, C.W, C.FLOOR_Y - 300))


ROOMS = [ReadingRoom, SlideArchive, LectureRoom]
