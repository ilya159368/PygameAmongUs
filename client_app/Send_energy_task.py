import pygame as pg


class Slider(pg.sprite.Sprite):
    image = pg.image.load('images/slider.png')

    def __init__(self, pos: tuple, size: tuple, screen, board_size: tuple):
        super().__init__()
        self.x, self.y = pos
        self.w, self.h = size
        self.screen = screen
        self.mouse_hover = False
        self.capture = False

        self.done = False

        self.board_x, self.board_y = board_size

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))

    def hover(self):
        pos = pg.mouse.get_pos()
        if self.x <= pos[0] <= self.x + self.w and self.y <= pos[1] <= self.y + self.h:
            self.mouse_hover = True
        else:
            self.mouse_hover = False

    def update(self):
        if self.capture:
            for e in pg.event.get(pg.MOUSEBUTTONUP):
                if e.button == 1:
                    self.capture = False
                    if e.pos[1] > self.board_y + 360:
                        self.y = self.board_y + 360
                    elif e.pos[1] < self.board_y + 286:
                        self.y = self.board_y + 286
                        self.done = True
                    else:
                        self.y = e.pos[1]

        self.hover()
        if self.mouse_hover:
            for e in pg.event.get(pg.MOUSEBUTTONDOWN):
                if e.button == 1:
                    self.capture = True


class SendEnergy(pg.sprite.Sprite):
    image = pg.image.load('images/send_energy.png')

    def __init__(self, pos: tuple, size: tuple, screen, special=None):
        super().__init__()
        self.x, self.y = pos
        self.w, self.h = size
        self.screen = screen

        self.slider = Slider((self.x + 317, self.y + 324), (44, 37), self.screen, (self.x, self.y))

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))
        self.slider.draw()

    def update(self):
        self.slider.update()


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

    task = SendEnergy((100, 100), (440, 441), screen)

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



