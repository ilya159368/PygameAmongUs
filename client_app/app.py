from os import environ
import pickle
from shared_files.protocol import *
from widgets import *
from collections import deque

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg


class App:
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
        # service attrs --------
        self.before_exit = []  # list of functions
        self.queue_to = deque()
        self.queue_from = deque()
        self.send_thread = None
        # end service attrs ----

        self.in_game = False
        self.offline = False
        self.connecting = True
        self.token = None
        self.screen = pg.display.set_mode([1280, 720])
        self.clock = pg.time.Clock()

        # CONSTANTS
        WHITE = (255, 255, 255)
        FONT_DEFAULT = pg.font.SysFont('monospace', 70)
        self.bg_img = pg.image.load('images/bg.png')
        self.back_img = pg.image.load('images/back.png')
        self.account_img = pg.image.load('images/account.png')

        self.menu_group = pg.sprite.Group()
        self.account_group = pg.sprite.Group()
        self.menu_btn_play = Button((200, 400), (300, 100), WHITE,
                                    TextLabel('play'),
                                    width=5, border_radius=True, group=self.menu_group)
        self.menu_btn_account = Button((25, 25), (100, 100), pg.SRCALPHA,
                                       self.account_img, group=self.menu_group,
                                       func=self.show_account)
        self.menu_linedit = LineEdit((600, 300), (300, 200), WHITE, width=5,
                                     placeholder='name...', border_radius=True,
                                     group=self.menu_group)
        self.account_btn_back = Button((25, 25), (100, 100), pg.SRCALPHA,
                                       self.back_img, group=self.account_group, func=self.show_menu)
        self.account_signin_login = LineEdit((100, 300), (500, 150), WHITE, width=5,
                                             placeholder='login', border_radius=True,
                                             group=self.account_group)
        self.account_signin_password = LineEdit((700, 300), (500, 150), WHITE, width=5,
                                                placeholder='password', border_radius=True,
                                                group=self.account_group)
        self.account_btn_back = Button((400, 550), (450, 100), WHITE,
                                       TextLabel('Sign in'), group=self.account_group, func=None, width=5, border_radius=True)
        # PREDEFINE
        self.visible_group = self.menu_group

    def resize_event(self):
        self.bg_img = pg.transform.smoothscale(self.bg_img, self.screen.get_size())
        pass

    def draw(self):
        self.screen.blit(self.bg_img, (0, 0))
        # self.screen.fill((255, 255, 255))

        self.visible_group.draw(self.screen)

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
                    self.to_queue(JoinRoomRequest(111))  # TODO: get token from gui
            # keyboard-holding
            keys = pg.key.get_pressed()
            if keys[pg.K_w]:
                self.to_queue(MouseClickRequest(0, 0))

            # drawing / recv
            if self.queue_from:
                resp = self.from_queue()
                if resp.operation == OperationsEnum.find_rooms:
                    # TODO: add rooms_list to listbox
                    rooms = resp.rooms_list
                    print(rooms)
                elif resp.operation in (OperationsEnum.create_room, OperationsEnum.join_room):
                    self.in_game = True
            self.draw()
            try:
                pg.display.flip()
                self.clock.tick(32)
            except KeyboardInterrupt:
                pass

    def show_menu(self):
        self.visible_group = self.menu_group

    def show_account(self):
        self.visible_group = self.account_group

    def show_game(self):
        pass


def main():
    pg.init()
    app = App()
    # connect = threading.Thread(target=Client, args=(app,))
    # connect.start()
    app.run()


if __name__ == '__main__':
    main()
