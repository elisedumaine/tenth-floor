"""Tenth Floor - the class game.

    python main.py                  # play the whole building
    python main.py --floor NAME     # practice your floor (floors/NAME.py): no clock, endless retries
"""
import argparse
import sys

import pygame

from engine import config as C
from engine.game import Game, keys_from_keyboard


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", help="practice one floor, by file name without .py")
    args = ap.parse_args()

    pygame.init()
    screen = pygame.display.set_mode((C.W, C.H), pygame.SCALED)
    pygame.display.set_caption("Tenth Floor")
    game = Game(practice_floor=args.floor)
    clock = pygame.time.Clock()
    while True:
        start = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                return 0
            if e.type == pygame.KEYDOWN and e.key == pygame.K_f:
                game.toggle_light()
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN):
                start = True
        dt = min(clock.tick(C.FPS) / 1000.0, 1 / 30)
        game.step(dt, keys_from_keyboard(), pressed_start=start)
        game.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    sys.exit(main())
