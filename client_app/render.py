import pygame
import math


__surface: pygame.surface.Surface
__fps = 60
__clock: pygame.time.Clock


def lerp(x1, x2, perc):
    return x1 + (x2 - x1) * perc


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other):
        return Vector2(self.x / other, self.y / other)

    def __itruediv__(self, other):
        self.x /= other
        self.y /= other

    def length(self):
        return math.sqrt(self.length_sqr())

    def __str__(self):
        return "%.5f, %.5f" % (self.x, self.y)

    def clamp(self, maxim):
        relative = self.length() / maxim
        if relative != 0:
            self.x = self.x / relative
            self.y = self.y / relative

    def length_sqr(self):
        return self.x ** 2 + self.y ** 2

    def copy(self):
        return Vector2(self.x, self.y)

    def to_pg(self):
        return (self.x, self.y)


class Image:
    def __init__(self, name):
        self.surface = pygame.image.load(name)
        self.surface.convert()
        self.rect = self.surface.get_rect()


class CollisionMap:
    def __init__(self, surface):
        self.mask = pygame.mask.from_surface(surface)
        self.image = pygame.Surface(surface.get_size())
        self.rect = self.image.get_rect()


def init(size: tuple[int, int] or list[int, int]) -> bool:
    global __surface
    global __clock

    try:
        __surface = pygame.display.set_mode(size)
        __clock = pygame.time.Clock()
        return True
    except:
        return False


def start_frame(color: pygame.Color or tuple[int, int, int] | str = (0, 0, 0)):
    __surface.fill(color)


def end_frame():
    pygame.display.flip()
    __clock.tick(__fps)


def set_fps(fps: int):
    global __fps
    __fps = fps


def rect(start: Vector2, end: Vector2, color: pygame.Color or tuple[int, int, int] or tuple[int, int, int, int] or str, width: int = 1, rounding: int = 0, group=None):
    pygame.draw.rect(__surface, color, (start.x, start.y, end.x - start.x, end.y - start.y), width=width, border_radius=rounding)


def rect_filled(start: Vector2, end: Vector2, color: pygame.Color or tuple[int, int, int] or tuple[int, int, int, int] or str, rounding: int = 0):
    pygame.draw.rect(__surface, color, (start.x, start.y, end.x - start.x, end.y - start.y), border_radius=rounding)


def circle(origin: Vector2, color: pygame.Color or tuple[int, int, int] or tuple[int, int, int, int] or str, radius: float or int, width:int = 1):
    pygame.draw.circle(__surface, color, (origin.x, origin.y), radius, width=width)


def circle_filled(origin: Vector2, color: pygame.Color or tuple[int, int, int] or tuple[int, int, int, int] or str, radius: float or int):
    pygame.draw.circle(__surface, color, (origin.x, origin.y), radius)


def image(image: Image, origin: Vector2 = Vector2(0, 0)):
    __surface.blit(image.surface, (origin.x, origin.y))


def load_image(name: str) -> Image:
    return Image(name)