import pygame

import render
import time

Vector2 = render.Vector2


def lerp(x1, x2, perc):
    return x1 + (x2 - x1) * perc


class Player:
    def __init__(self):
        self.alive = True
        self.imposter = False
        self.origin = Vector2(4800, 1500)
        self.last_origin = Vector2(0, 0)
        self.abs_origin = Vector2(0, 0) # для интерполяции
        self.velocity = Vector2(0, 0)
        self.color = 0 # пригодится в будущем
        self.id = 0
        self.name = ""
        self.last_net_update = 0.0
        self.side = False
        self.rect = (0, 0, 0, 0)
        self.image = pygame.Surface((30, 30))

    def net_update(self, origin, velocity):
        self.last_origin = self.origin.copy()
        self.origin = origin
        self.velocity = velocity
        if self.velocity.x != 0:
            self.side = self.velocity.x > 0
        self.last_net_update = time.time()

    def frame_update(self):
        frame_fraction = (time.time() - self.last_net_update) * 16
        self.abs_origin.x = lerp(self.last_origin.x, self.origin.x, frame_fraction)
        self.abs_origin.y = lerp(self.last_origin.y, self.origin.y, frame_fraction)

    def get_collision_rect(self, origin):
        mins = origin - Vector2(15, 30)
        maxs = origin + Vector2(15, 0)
        return (mins.x, mins.y, maxs.x, maxs.y)