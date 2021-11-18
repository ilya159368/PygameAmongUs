from os import environ
import pickle
from protocol import *
from client import Client
from widgets import *
from collections import deque
from thread_ import CustomThread
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg


class App:
    before_exit = []  # functions
    in_game = False
    offline = False

    queue_to = None
    queue_from = None
    send_thread = None

    def __init__(self):
        self.screen = pg.display.set_mode([1280, 720])
        self.clock = pg.time.Clock()

        # CONSTANTS
        self.BG = pg.image.load('images/bg.png')
        self.menu_group = pg.sprite.Group()
        self.menu_btn_play = Button((300, 300), (200, 200), self.menu_group)

        # PREDEFINE
        self.visible_group = self.menu_group

    def resize_event(self):
        self.BG = pg.transform.scale(self.BG, self.screen.get_size())

    def draw(self):
        self.screen.blit(self.BG, (0, 0))
        self.visible_group.draw(self.screen)
        pg.display.flip()

    def to_queue(self, req):
        if self.offline:
            return
        if self.send_thread.is_paused():
            self.send_thread.resume()
        self.queue_to.append(pickle.dumps(req))

    def from_queue(self):
        if self.offline:
            return
        return pickle.loads(self.queue_from.popleft())

    def run(self):
        while 1:
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
                    self.in_game = True
                elif e.type == pg.KEYDOWN and e.key == pg.K_f:
                    self.to_queue(FindRoomsRequest())
                elif e.type == pg.KEYDOWN and e.key == pg.K_j:
                    self.to_queue(JoinRoomRequest('name'))  # TODO: get name from gui
            # drawing / recv
            if self.queue_from:
                resp = self.from_queue()
                if resp.operation == OperationsEnum.find_rooms:
                    # TODO: add rooms_list to listbox
                    rooms = resp.rooms_list
                    print(rooms)
            self.draw()
            self.clock.tick(30)

    def add_before_exit(self, func):
        self.before_exit.append(func)


def main():
    queue_to = deque()
    queue_from = deque()
    app = App()
    app.queue_from = queue_from
    app.queue_to = queue_to
    try:
        client = Client()
        client.queue_from = queue_from
        client.queue_to = queue_to

        send_thread = CustomThread(target=client.send_data)
        send_thread.start()

        app.send_thread = send_thread

        app.add_before_exit(client.close)
        app.add_before_exit(send_thread.kill)
    except ConnectionRefusedError:
        app.offline = True
        print('Server disabled')

    app.run()


if __name__ == '__main__':
    main()
