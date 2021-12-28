import pygame as pg


class Vent:
    def __init__(self, pos, camera_pos):
        self.pos = pos
        self.camera_pos = camera_pos

    def update(self):
        for e in pg.event.get(pg.KEYDOWN):
            if e.key == pg.K_RIGHT:
                ...
            elif e.key == pg.K_LEFT:
                ...