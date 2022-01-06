import pygame as pg
from widgets import Button, ListWidget, Text
# from app import FONT_DEFAULT


class Voting:
    def __init__(self, x, y, w, h, screen, players):
        self.players = players
        self.screen = screen

        self.x = x
        self.y = y

        self.w = w
        self.h = h

    def draw(self):
        players = [Button((1, 1), (self.w // 3, self.h // 7), color, Text(
            name, full_font=FONT_DEFAULT
        )) for color, name in self.players.items()]
        pls = pg.sprite.Group()

        widget = ListWidget((self.x, self.y), (self.w, self.h), 'white', border_color='gray',
                            scrollbar=False)
        widget.extend(players)

        widget.draw()


if __name__ == '__main__':

    pg.init()
    FONT = pg.font.SysFont('Roboto', 50)
    pg.key.set_repeat(200, 70)
    FPS = 50
    WIDTH = 1024
    HEIGHT = 768
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    all_sprites = pg.sprite.Group()
    running = True
    FONT_DEFAULT = pg.font.SysFont('monospace', 70)
    # wires = WiresTask((WIDTH // 2 - WIDTH // 8, HEIGHT // 2 - HEIGHT // 6), (WIDTH // 4, HEIGHT // 3), screen)
    voting = Voting(200, 200, 500, 700, screen, {(255, 0, 0): 'первый', (0, 255, 0): 'второй', (0, 0, 255): 'третий'})

    while running:
        WIDTH, HEIGHT = pg.display.get_window_size()
        # voting.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill(pg.Color(0, 0, 0))
        voting.draw()

        pg.display.flip()
        clock.tick(FPS)
