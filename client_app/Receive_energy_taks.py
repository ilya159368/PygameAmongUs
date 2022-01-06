import pygame as pg


class ReceiveEnergy(pg.sprite.Sprite):
    image = pg.image.load('images/start.png')

    def __init__(self, pos: tuple, size: tuple, screen):
        super().__init__()
        self.x, self.y = pos
        self.w, self.h = size
        self.screen = screen

        self.done = False

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))

    def update(self):
        for e in pg.event.get(pg.MOUSEBUTTONUP):
            if e.button == 1:
                if 274 + self.x < e.pos[0] < 290 + self.x and 139 + self.y < e.pos[1] < 202 + self.y:
                    self.image = pg.image.load('images/done.png')
                    self.done = True


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
    task = ReceiveEnergy((100, 100), (559, 333), screen)

    while running:
        task.update()
        WIDTH, HEIGHT = pg.display.get_window_size()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill(pg.Color(0, 0, 0))
        task.draw()
        pg.display.flip()
        clock.tick(FPS)