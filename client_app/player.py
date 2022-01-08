import pygame
import math

import render
import time

Vector2 = render.Vector2
Color = pygame.Color

pygame.init()


def load_amogus_image(name, size=(100, 120)):
    fullname = "images/Player - Among Us/Individual Sprites/" + name
    # image = Image.open(fullname)
    # image = utils.color_to_alpha(image, (0, 0, 0, 255))
    # raw_str = image.tobytes("raw", 'RGBA')
    # surface = pygame.image.fromstring(raw_str, image.size, 'RGBA')
    surface = pygame.image.load(fullname)
    return pygame.transform.scale(surface, size)


anims = {
    "walk": [
        load_amogus_image("Walk/walk1.png"),
        load_amogus_image("Walk/walk2.png"),
        load_amogus_image("Walk/walk3.png"),
        load_amogus_image("Walk/walk4.png"),
        load_amogus_image("Walk/walk5.png"),
        load_amogus_image("Walk/walk6.png"),
        load_amogus_image("Walk/walk7.png"),
        load_amogus_image("Walk/walk8.png"),
        load_amogus_image("Walk/walk9.png"),
        load_amogus_image("Walk/walk10.png"),
        load_amogus_image("Walk/walk11.png"),
        load_amogus_image("Walk/walk12.png")
    ],
    "dead": load_amogus_image("Death/Dead0033.png", (100, 100))
}
idle = pygame.transform.scale(pygame.image.load("images/amogus.png"), (100, 120))


def lerp(x1, x2, perc):
    return x1 + (x2 - x1) * perc


def clamp(v, min, max):
    if v > max:
        v = max
    if v < min:
        v = min
    return v


class Player:
    def __init__(self):
        self.alive = True
        self.imposter = False
        self.origin = Vector2(4800, 1500)
        self.last_origin = Vector2(0, 0)
        self.abs_origin = Vector2(0, 0)  # для интерполяции
        self.velocity = Vector2(0, 0)
        self.color = (0, 0, 0)  # пригодится в будущем
        self.id = 0
        self.name = ""
        self.last_net_update = 0.0
        self.side = False
        self.rect = (0, 0, 0, 0)
        self.image = pygame.Surface((30, 30))
        self.walk_animation_left = []
        self.walk_animation_right = []
        self.idle_animation = []
        self.frames = 0
        self.interact_range = 120

    def net_update(self, origin, velocity):
        self.last_origin = self.origin.copy()
        self.origin = origin
        self.velocity = velocity
        if self.velocity.x != 0:
            self.side = self.velocity.x > 0
        self.last_net_update = time.time()
        self.frames += 1

    def frame_update(self):
        frame_fraction = (time.time() - self.last_net_update) * 16
        if frame_fraction > 1:
            frame_fraction = 1
        self.abs_origin.x = lerp(self.last_origin.x, self.origin.x, frame_fraction)
        self.abs_origin.y = lerp(self.last_origin.y, self.origin.y, frame_fraction)

    def get_collision_rect(self, origin):
        mins = origin - Vector2(15, 30)
        # maxs = origin + Vector2(15, 0)
        return (mins.x, mins.y, 30, 30)  # TODO check

    def load_anims(self):
        color = self.color
        for x in range(100):
            for y in range(120):
                pixel = idle.get_at((x, y))
                if pixel == (255, 0, 0):
                    idle.set_at((x, y), (clamp(color[0] - 50, 0, 255), clamp(color[1] - 50, 0, 255), clamp(color[2] - 50, 0, 255), 255))
        self.idle_animation = [
            pygame.transform.flip(idle, True, False),
            idle
        ]
        for anim in anims["walk"]:
            for x in range(100):
                for y in range(120):
                    pixel = anim.get_at((x, y))
                    if pixel == (255, 0, 0):
                        anim.set_at((x, y), (clamp(color[0] - 50, 0, 255), clamp(color[1] - 50, 0, 255), clamp(color[2] - 50, 0, 255), 255))
            self.walk_animation_left.append(pygame.transform.flip(anim, True, False))
            self.walk_animation_right.append(anim)
        for x in range(100):
            for y in range(100):
                pixel = anims["dead"].get_at((x, y))
                if pixel == (255, 0, 0):
                    anims["dead"].set_at((x, y), (clamp(color[0] - 50, 0, 255), clamp(color[1] - 50, 0, 255), clamp(color[2] - 50, 0, 255), 255))

    def get_image(self):
        if not self.alive:
            return anims["dead"]
        if self.side:
            if self.velocity.length_sqr() > 0:
                return self.walk_animation_right[self.frames % 10]
            else:
                return self.idle_animation[1]
        else:
            if self.velocity.length_sqr() > 0:
                return self.walk_animation_left[self.frames % 10]
            else:
                return self.idle_animation[0]

    def set_meet_point(self):
        self.origin = Vector2(4832 + math.cos(self.id * 36) * 300, 1080 + math.sin(self.id * 36) * 300)

