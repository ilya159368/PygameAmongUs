import pygame as pg


class Button(pg.sprite.Sprite):
    def __init__(self, pos: tuple, size: tuple, group):
        super(Button, self).__init__(group)
        self.rect = pg.rect.Rect(*pos, *size)
        self.image = pg.surface.Surface(size)
        self.image.fill(pg.Color(255, 255, 255))
        # self.image = pg.image.load('images/yandex.jpg')
