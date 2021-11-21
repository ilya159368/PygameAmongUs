import threading
from os import environ
import pickle
from shared_files.protocol import *
from client import Client
from widgets import *
from collections import deque
import array
import cairo
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import pygame_menu as pgm


class App:
    # service attrs --------
    before_exit = []  # list of functions
    queue_to = deque()
    queue_from = deque()
    send_thread = None
    # end service attrs ----

    in_game = False
    offline = False
    connecting = True
    token = None

    # service funcs ------------------
    def add_before_exit(self, func):
        self.before_exit.append(func)

    def to_queue(self, req):
        if self.offline or self.connecting:
            return
        if self.send_thread.is_paused():
            self.send_thread.resume()
        req.__setattr__('in_game', self.in_game)
        self.queue_to.append(pickle.dumps(req))

    def from_queue(self):
        if self.offline:
            return
        return pickle.loads(self.queue_from.popleft())
    # end service funcs --------------

    def __init__(self):
        self.screen = pg.display.set_mode([1280, 720])
        self.clock = pg.time.Clock()

        # CONSTANTS
        WHITE = (255, 255, 255)
        FONT_DEFAULT = pg.font.SysFont('monospace', 70)
        self.BG = pg.image.load('images/bg.png')
        # self.BG2 = pg.surface.Surface((1920, 1080))
        # self.BG2.fill((255, 255, 255))
        self.button_play = pg.image.load('images/button_play.svg')
        self.menu_group = pg.sprite.Group()
        self.menu_btn_play = Button((200, 400), (300, 100), self.menu_group, WHITE,
                                    TextLabel('play'),
                                    width=5, border_radius=True, disabled=True)
        self.menu_linedit = LineEdit((600, 300), (300, 200), self.menu_group, WHITE, width=5,
                                     placeholder='name...', border_radius=True)
        # PREDEFINE
        self.visible_group = self.menu_group

    def resize_event(self):
        self.BG = pg.transform.scale(self.BG, self.screen.get_size())
        self.button_play = pg.transform.smoothscale(self.button_play, (2000, 500))

    def draw(self):
        # self.screen.blit(self.BG2, (0, 0))
        self.screen.blit(self.BG, (0, 0))
        self.screen.blit(self.button_play, (600, 550))

        self.visible_group.draw(self.screen)
        pg.display.flip()

    def update(self):
        self.visible_group.update()

    def run(self):
        while 1:
            self.update()
            # events / send
            e: pg.event.Event
            for e in pg.event.get():
                # system
                if e.type == pg.QUIT:
                    [func() for func in self.before_exit]
                    exit()
                elif e.type in (pg.WINDOWRESIZED, pg.WINDOWSHOWN):
                    self.resize_event()
                # gameplay
                elif e.type == pg.MOUSEBUTTONDOWN:
                    self.to_queue(MouseClickRequest(*pg.mouse.get_pos()))
                elif e.type == pg.KEYDOWN and e.key == pg.K_c and not self.in_game:
                    self.to_queue(CreateRoomRequest('name', 10))
                elif e.type == pg.KEYDOWN and e.key == pg.K_f:
                    self.to_queue(FindRoomsRequest())
                elif e.type == pg.KEYDOWN and e.key == pg.K_j:
                    self.to_queue(JoinRoomRequest(111))  # TODO: get name from gui
            # keyboard-holding
            keys = pg.key.get_pressed()
            if keys[pg.K_w]:
                self.to_queue(MouseClickRequest(0, 0))

            # drawing / recv
            if self.queue_from:
                resp = self.from_queue()
                if resp.operation == OperationsEnum.find_rooms:
                    # TODO: add rooms_list to listbox and ROOMS ARE DIRTY SPRITES WITH NO UPDATING
                    rooms = resp.rooms_list
                    print(rooms)
                elif resp.operation in (OperationsEnum.create_room, OperationsEnum.join_room):
                    self.in_game = True
            self.draw()
            self.clock.tick(32)


def main():
    pg.init()
    app = App()
    connect = threading.Thread(target=Client, args=(app,))
    connect.start()
    app.run()


if __name__ == '__main__':
    main()
