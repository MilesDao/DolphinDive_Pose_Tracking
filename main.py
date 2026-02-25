import os
import sys
import pygame as pg

from game import play_flappy_bird

os.environ["SDL_VIDEO_CENTERED"] = '1'

if __name__ == "__main__":
    pg.init()
    pg.display.set_caption('FlappyBird Game')
    play_flappy_bird()
    pg.quit()
    sys.exit()
