import random

import pygame as pg
from random import shuffle
from widgets import Button, Text, SurfaceSprite

"""
5813
2721
86
181 карта в навигации

6147
3721
140
123 щиты

4910
4170
100
200 нижний мусор

5523
528
157
150 верхний мусор

5407
335
79
127 провода справа столовая

3830
270
110
110 провода слева столовая

4407
905
536
430 кнопка собрания

5548
1286
100
80 люк столовая

2870
1986
100
80 люк медкомната

2030
775
100
80 люк верхний двигатель

1690
674
90
110 провода верхний двигатель

1200
1810
70
100 провода реактор

845
1788
100
80 люк реактор верхний

742
1679
70
76 цифры реактор

1037
2477
100
80 люк реактор нижний


"""
"""

class NumbersTask(SurfaceSprite):
    def __init__(self, size, pos: tuple, screen, color):
        super().__init__(pos, size, color)
        self.cell = size[1] // 2

        self.PRESSED = (33, 194, 135)
        self.DEFAULT = (135, 152, 198)

        self.screen = screen
        f = list(range(1, 6))
        s = list(range(6, 11))
        shuffle(f)
        shuffle(s)
        self.nums = [f, s]
        self.field: [Button] = pg.sprite.Group()
        self.prev_num = 0

        self.create()

    def draw(self):
        super().draw()
        
        pg.draw.rect(self.screen, 'black', (self.x - self.size // 4, self.y - self.size // 4,
                                            self.w + self.size // 2, self.h + self.size // 2), 0)

        pg.draw.rect(self.screen, (155, 155, 155), (self.x - self.size // 5, self.y - self.size // 5,
                                                    self.w + self.size // 2.5, self.h + self.size // 2.5), 0)

        for i in range(2):
            for j in range(5):

                pg.draw.rect(self.screen, (135, 152, 198),
                             (self.x + self.size * j, self.y + self.size * i, self.size, self.size), 0)

                pg.draw.rect(self.screen, (11, 62, 190),
                             (self.x + self.size * j, self.y + self.size * i, self.size, self.size), 4)

                font = FONT.render(str(self.field[i][j]), True, (16, 32, 84))

                self.screen.blit(font, (
                    self.x + self.size * j + self.size // 2 - font.get_width() // 2,
                    self.y + self.size * i + self.size // 2 - font.get_height() // 2 + 4,
                    self.size, self.size))

        pg.draw.rect(self.screen, (11, 62, 190), (self.x, self.y, self.w, self.h), 4)
        x, y = self.pos
        w, h = self._size

        pg.draw.rect(self.screen, 'black', (x - self.cell // 4, y - self.cell // 4,
                                            w + self.cell // 2, h + self.cell // 2), 0)

        pg.draw.rect(self.screen, (155, 155, 155), (x - self.cell // 5, y - self.cell // 5,
                                                    w + self.cell // 2.5, h + self.cell // 2.5), 0)
        for i in self.field.sprites():
            i.draw()
            # self.screen.blit(i.image, i.rect)
        pg.draw.rect(self.image, (11, 62, 190), (0, 0, *self._size), 8)
        self.screen.blit(self.image, self.rect)
        self.field.draw(self.screen)

    def create(self):
        self.field.add([Button((i * self.cell + self.pos[0], j * self.cell + self.pos[1]), (self.cell, self.cell), self.DEFAULT,
                               Text(str(self.nums[j][i]), full_font=FONT, color=(16, 32, 84)),
                               border_color=(11, 62, 190), width=4,
                               func=self.click(str(self.nums[j][i]), i + j * 5), handle_hover=False, handle_disabled=False)
                        for j in range(2) for i in range(5)])

    def click(self, num: str, index):
        def __inner():
            btn: Button = self.field.sprites()[index]
            if int(btn.text_label.text) == self.prev_num + 1:
                btn.color = self.PRESSED
                self.prev_num += 1
                btn.set_disabled(True)
            else:
                for i in self.field.sprites():
                    i.color = self.DEFAULT
                    i.set_disabled(False)
                self.prev_num = 0
        return __inner

    def update(self):
        for i in self.field.sprites():
            i.update()
"""
from random import shuffle
from widgets import ListWidget


class NumbersTask:
    def __init__(self, x, y, size, screen, font):
        self.x = x
        self.y = y
        self.size = size
        self.w = w = size * 5
        self.h = h = size * 2

        self.center = ((x * 2 + w) // 2, (y * 2 + h) // 2)

        self.font = font

        self.screen = screen
        f = list(range(1, 11))
        shuffle(f)
        self.field = [f[0:5], f[5:]]
        self.pressed = [[[j, 0] for j in i] for i in self.field[::]]
        self.last_pressed = 0

    def draw(self):
        pg.draw.rect(self.screen, 'black', (self.x - self.size // 4, self.y - self.size // 4,
                                            self.w + self.size // 2, self.h + self.size // 2), 0)

        pg.draw.rect(self.screen, (155, 155, 155), (self.x - self.size // 5, self.y - self.size // 5,
                                                    self.w + self.size // 2.5, self.h + self.size // 2.5), 0)

        for i in range(2):
            for j in range(5):
                if not self.pressed[i][j][1]:
                    pg.draw.rect(self.screen, (135, 152, 198),
                                 (self.x + self.size * j, self.y + self.size * i, self.size, self.size), 0)
                else:
                    pg.draw.rect(self.screen, (33, 194, 135),
                                 (self.x + self.size * j, self.y + self.size * i, self.size, self.size), 0)

                pg.draw.rect(self.screen, (11, 62, 190),
                             (self.x + self.size * j, self.y + self.size * i, self.size, self.size), 4)

                font = self.font.render(str(self.field[i][j]), True, (16, 32, 84))

                self.screen.blit(font, (
                    self.x + self.size * j + self.size // 2 - font.get_width() // 2,
                    self.y + self.size * i + self.size // 2 - font.get_height() // 2 + 4,
                    self.size, self.size))

        pg.draw.rect(self.screen, (11, 62, 190), (self.x, self.y, self.w, self.h), 4)

    def click(self, pos):
        if self.get_cell(pos):
            x, y = self.get_cell(pos)
            if self.field[y][x] == self.last_pressed + 1:
                self.pressed[y][x][1] = 1
                self.last_pressed += 1
            elif self.pressed == 10:
                self.last_pressed = 0
                self.pressed = [[[self.pressed[i][j], 0] for j in range(5)] for i in range(2)]
                # тут типо тоже выход
            else:
                self.last_pressed = 0
                self.pressed = [[[self.pressed[i][j], 0] for j in range(5)] for i in range(2)]  # тут типо выход

    def get_cell(self, pos):
        x, y = (pos[0] - self.x) // self.size, (pos[1] - self.y) // self.size
        if 5 >= x + 1 > 0 and 2 >= y + 1 > 0:
            return x, y
        return False

    def update(self):
        for e in pg.event.get(pg.MOUSEBUTTONDOWN):
            if e.button == 1:
                self.click(e.pos)


class WiresTask:

    bg = pg.image.load('images/wires.png')

    def __init__(self, pos, size, screen):
        self.size = size
        self.pos = pos
        self.center = ((self.pos[0] * 2 + self.size[0]) // 2, (self.pos[1] * 2 + self.size[1]) // 2)
        self.screen = screen
        self.left_wires = ['red', 'yellow', 'pink', 'blue']
        self.right_wires = self.left_wires.copy()
        random.shuffle(self.left_wires)
        random.shuffle(self.right_wires)
        self.bg = pg.transform.smoothscale(self.bg, self.size)

        x, y = self.pos
        w, h = self.size
        width = w // 10
        self.height = height = h // 16
        self.left_rects = [(x, y + (i + 1) * h // 5, width, height) for i in range(4)]
        self.right_rects = [(x + w - width, y + (i + 1) * h // 5, width, height) for i in range(4)]

        self.to_draw_line = False
        self.start = None
        self.active_color = None
        self.drew_lines = []

    def draw(self):
        self.screen.blit(self.bg, self.pos)
        [pg.draw.rect(self.screen, self.left_wires[i], self.left_rects[i]) for i in range(4)]
        [pg.draw.rect(self.screen, self.right_wires[i], self.right_rects[i]) for i in range(4)]
        if self.to_draw_line:
            pg.draw.line(self.screen, self.active_color, self.start, pg.mouse.get_pos(), self.height)
        for line in self.drew_lines:
            pg.draw.line(self.screen, *line, self.height)

    def update(self):
        for e in pg.event.get(pg.MOUSEBUTTONDOWN):
            if e.button == 1:
                for ind, el in enumerate(self.left_rects):
                    if el[0] <= e.pos[0] <= el[0] + el[2] and el[1] <= e.pos[1] <= el[1] + el[3]:
                        self.to_draw_line = True
                        self.start = ((el[0] * 2 + el[2]) // 2, (el[1] * 2 + el[3]) // 2)
                        self.active_color = self.left_wires[ind]
                        break
        for e in pg.event.get(pg.MOUSEBUTTONUP):
            if e.button == 1:
                for ind, el in enumerate(self.right_rects):
                    if el[0] <= e.pos[0] <= el[0] + el[2] and el[1] <= e.pos[1] <= el[1] + el[3]:
                        self.drew_lines.append((self.active_color, self.start, ((el[0] * 2 + el[2]) // 2, (el[1] * 2 + el[3]) // 2)))
                        break
            self.to_draw_line = False


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
    # wires = WiresTask((WIDTH // 2 - WIDTH // 8, HEIGHT // 2 - HEIGHT // 6), (WIDTH // 4, HEIGHT // 3), screen)
    # button = Button((100, 100), (50, 100), (255, 0, 0), Text('btn', color=(255, 255, 255)), width=20,
                    # border_color=(255, 255, 255))
    widget = ListWidget((100, 100), (200, 500), (255, 255, 255), border_color=(255, 0, 0), width=5, border_radius=90)

    while running:
        WIDTH, HEIGHT = pg.display.get_window_size()
        # wires.update()
        widget.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        widget.draw()
        screen.fill(pg.Color(0, 0, 0))
        # wires.draw()

        pg.display.flip()
        clock.tick(FPS)
