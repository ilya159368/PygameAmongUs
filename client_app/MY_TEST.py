import pygame as pg

from protocol import Token
from player import Player
from widgets import Button, Text
from timer import Timer


class PlayerProfile(pg.sprite.Sprite):
    image = None

    def __init__(self, pos: tuple, size: tuple, player, screen, imp):
        super().__init__()
        self.x = pos[0]
        self.y = pos[1]
        self.screen = screen

        self.w = size[0]
        self.h = size[1]

        self.color = player.color
        self.id = player.id
        self.name = player.name
        self.imp = imp
        self.alive = player.alive
        self.image = pg.transform.smoothscale(player.voting_img, player.voting_img.get_size())
        self.me_imp = player.imposter

        self.mouse_hover = False
        self.selected = False
        self.voted = False
        if self.alive:
            self.active = True
        else:
            self.active = False

        self.font = pg.font.Font(None, int(self.h // 1.5))

        if imp and self.me_imp:
            self.font_render = self.font.render(self.name, 1, 'red')
        else:
            self.font_render = self.font.render(self.name, 1, (15, 15, 38))

        # self.confirm = pg.image.load('images/confirm.png')
        # self.cancel = pg.image.load('images/cancel.png')

        self.vote = pg.image.load('images/voted.png')
        self.rect = pg.Rect(self.x, self.y, self.w, self.h)

    def draw(self):
        if self.mouse_hover and self.alive and not self.selected and self.active:
            pg.draw.rect(self.screen, 'gray', (self.x, self.y, self.w, self.h), 0, border_radius=15)
        else:
            pg.draw.rect(self.screen, (238, 243, 249), (self.x, self.y, self.w, self.h), 0, border_radius=15)

        if not self.alive:
            pg.draw.rect(self.screen, pg.color.Color(41, 41, 41), (self.x, self.y, self.w, self.h), 0, border_radius=15)
            self.font_render = self.font.render(self.name, 1, (255, 255, 255))

        if self.selected:
            pg.draw.rect(self.screen, (142, 244, 141), (self.x, self.y, self.w, self.h), 0, border_radius=15)
            self.screen.blit(self.font_render, self.font_render.get_rect().move(  # отрисовка имени
                self.x + 1.5 * self.image.get_width(), self.y + self.h // 5))

        self.screen.blit(self.image, self.image.get_rect().move(self.x + 5, self.y + 5))  # иконка игрока

        if self.voted:
            self.screen.blit(self.vote, self.image.get_rect().move(self.x + 5, self.y + 5))
        # if self.selected:
        #     self.screen.blit(self.confirm, self.confirm.get_rect().move(self.x + self.w - 55, self.y + self.h - 50))
        #     self.screen.blit(self.cancel, self.cancel.get_rect().move(self.x + self.w - 110, self.y + self.h - 50))
        self.screen.blit(self.font_render, self.font_render.get_rect().move(  # отрисовка имени
            self.x + 1.5 * self.image.get_width(), self.y + self.h // 5))

    def check_hover(self):
        pos = pg.mouse.get_pos()
        if self.x <= pos[0] <= self.x + self.w and self.y <= pos[1] <= self.y + self.h:
            self.mouse_hover = True
        else:
            self.mouse_hover = False

    # def select(self):
    #     for e in pg.event.get(pg.MOUSEBUTTONUP):
    #         if e.button == 1:
    #             self.selected = not self.selected
    #             break

    def update(self):
        self.check_hover()
        if self.mouse_hover and self.active:
            for e in pg.event.get(pg.MOUSEBUTTONUP):
                if e.button == 1:
                    self.selected = True
                    break


class VotingList(pg.sprite.Sprite):
    image = pg.image.load('images/tablet.png')

    def __init__(self, pos: tuple, size: tuple, players: list, screen, imp, send_func, alive):
        super().__init__()
        # ____РАСПОЛОЖЕНИЕ ТАБЛЕТА С КНОПКАМИ____
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]
        self.screen = screen
        self.alive = alive
        # ____РАСПРЕДЕЛЕНИЕ ИГРОКОВ____
        self.players = players
        self.profiles = []

        self.imp = imp  # я импостер?
        # ____кнопка скипа____
        img = pg.image.load('images/skip_vote.png')
        pg.transform.smoothscale(img, (self.w // 12, self.h // 20))
        self.skip = False

        self.skip_btn = Button((self.x + 50, self.y + self.h - 100), (True, True), pg.SRCALPHA,
                               img, paddings_factor=(1, 1), image_scale_type=0, hovered_color=(210, 210, 210),
                               func=self.make_skip, handle_disabled=False)
        # ____кнопка чата____
        # img1 = pg.image.load('images/chat_button.png')
        # self.chat_btn = Button((self.x + self.w - 150, self.y + 50), (True, True), pg.SRCALPHA,
        #                        img1, paddings_factor=(1, 1), image_scale_type=0, hovered_color=(210, 210, 210),
        #                        handle_disabled=False)
        # ________
        self.choice = None  # выбор игрока
        self.send_func = send_func

        self.timer = Timer((self.x + 670, self.y + 490), (100, 50), self.screen, 'black', 60)
        self.fill_profiles()
        if not self.alive:
            self.make_skip()
        # ____КОНЕЦ ЧАСТИ ПЛАНШЕТА____

    def draw(self):
        self.screen.blit(self.image, self.image.get_rect().move(self.x, self.y))
        for profile in self.profiles:
            profile.update()
            profile.draw()
        self.screen.blit(self.skip_btn.image, self.skip_btn.rect)
        # self.screen.blit(self.chat_btn.image, self.chat_btn.rect)
        if self.timer.r >= 0:
            self.timer.draw()

    def fill_profiles(self):
        half1 = self.players[:len(self.players) - len(self.players) // 2]
        half2 = self.players[len(self.players) - len(self.players) // 2:]

        for i in range(len(max([half1, half2], key=len))):

            if i < len(half1):
                self.profiles.append(
                    PlayerProfile(
                        (self.x + self.w // 9, self.y + self.h // 10 * (i + 2) + self.h // 15 * i),
                        (self.w // 3, self.h // 10), half1[i], self.screen, self.imp))

            if i < len(half2):
                self.profiles.append(
                    PlayerProfile(
                        (self.x + self.w // 2, self.y + self.h // 10 * (i + 2) + self.h // 15 * i),
                        (self.w // 3, self.h // 10), half2[i], self.screen, self.imp))

    def update(self):
        if any([pl.selected for pl in self.profiles]) and self.choice is None:
            for player in self.profiles:
                player.active = False
                if player.selected:  # игрок выбран
                    self.choice = int(player.id)
                    self.send_func(self.choice)
            self.skip_btn.set_disabled(True)

        self.skip_btn.update()

    def make_voted(self, id_):
        for pl in self.profiles:
            if pl.id == id_:
                pl.voted = True

    def make_skip(self):
        self.choice = 'skip'
        for player in self.profiles:
            player.active = False
        self.skip_btn.set_disabled(True)
        if self.alive:
            self.send_func(None)


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

    # player = PlayerProfile((100, 100), (200, 60), all_sprites, 'default', 'guy', screen)
    players = [Player(), Player(), Player()]
    players[0].imposter = True
    players[1].alive = False

    players[0].name = 'imposter'
    players[1].name = 'dead'
    players[2].name = 'guy3'

    tablet = VotingList((100, 100), (853, 582), players, screen, False, True)
    tablet.make_voted('guy3')

    while running:
        tablet.update()

        WIDTH, HEIGHT = pg.display.get_window_size()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill(pg.Color(0, 0, 0))
        tablet.draw()
        pg.display.flip()
        clock.tick(FPS)