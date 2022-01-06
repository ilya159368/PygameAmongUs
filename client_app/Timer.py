import time
import pygame as pg


class Timer:
    def __init__(self, pos: tuple, size: tuple, screen, color, countdown):
        self.x, self.y = pos
        self.w, self.h = size
        self.screen = screen
        self.color = color

        self.font = pg.font.Font(None, int((self.w + self.h) // 2))
        self.count = countdown
        self.start_time = time.time()

    def draw(self):
        r = int(self.count - (time.time() - self.start_time))
        if r >= 0:
            self.screen.blit(self.font.render(str(r), 1, self.color), (self.x, self.y))


class ProgressBar:
    def __init__(self, pos: tuple, size: tuple, screen, segments):
        self.x, self.y = pos
        self.w, self.h = size
        self.screen = screen

        self.segments = segments  # количество сегментов
        self.segment_len = self.w // segments  # длина сегмента
        self.completed = 0  # количество залитых сегментов

    def draw(self):
        pg.draw.rect(self.screen, 'gray', (self.x, self.y, self.w, self.h), 5)
        pg.draw.rect(self.screen, 'green', (self.x, self.y, self.segment_len * self.completed, self.h))
        for segment in range(self.segments + 1):
            pg.draw.rect(self.screen, 'gray', (self.x + segment * self.segment_len, self.y, 3, self.h), 0)


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

    # task = SendEnergy((100, 100), (440, 441), screen)
    # timer = Timer((100, 100), (50, 50), screen, 'white', 60)
    bar = ProgressBar((100, 100), (700, 50), screen, 50)
    while running:
        # timer.update()
        WIDTH, HEIGHT = pg.display.get_window_size()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    bar.completed += 1
                if event.button == 3:
                    bar.completed -= 1

        screen.fill(pg.Color(0, 0, 0))
        # timer.draw()
        bar.draw()
        pg.display.flip()
        clock.tick(FPS)
