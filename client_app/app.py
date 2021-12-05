import time
from os import environ
import pickle
from shared_files.protocol import *
from widgets import *
from collections import deque
import keyboard
import player
import render
import threading

Vector2 = render.Vector2

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
        self.screen = pg.display.set_mode([1600, 900])
        render.init((1600, 900))
        self.clock = pg.time.Clock()
        self.player_list = [player.Player()]
        self.camera_pos = Vector2(0, 0)
        self.last_update_time = 0

        # CONSTANTS
        WHITE = (255, 255, 255)
        FONT_DEFAULT = pg.font.SysFont('monospace', 70)
        self.bg_img = pg.image.load('images/bg.png')
        self.back_img = pg.image.load('images/back.png')
        self.account_img = pg.image.load('images/account.png')
        self.map_image = pg.image.load("images/among_map.png")
        self.amogus_left = pg.image.load("images/amogus.png")
        self.amogus_right = pg.image.load("images/amogus.png")
        self.amogus_left = pygame.transform.smoothscale(self.amogus_left, (100, 120))
        self.amogus_right = pygame.transform.smoothscale(self.amogus_right, (100, 120))
        self.amogus_left = pygame.transform.flip(self.amogus_left, True, False)
        self.collision_map = render.CollisionMap(pg.image.load("images/among_walls.png"))

        self.menu_group = pg.sprite.Group()
        self.account_group = pg.sprite.Group()
        self.game_group = pg.sprite.Group()
        self.menu_btn_play = Button((200, 400), (300, 100), WHITE,
                                    TextLabel('play'),
                                    width=5, border_radius=True, group=self.menu_group, func=self.show_game)
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
        if not self.in_game:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.map_image, self.world_to_screen(Vector2(0, 0)).to_pg())
            if time.time() - self.last_update_time > 1/16:
                self.cl_move()
                self.last_update_time = time.time()
            self.draw_players()
        self.visible_group.draw(self.screen)

    def update(self):
        self.visible_group.update()

    def draw_players(self):
        for player in self.player_list:
            player.frame_update()
            self.camera_pos = player.abs_origin
            w2s = self.world_to_screen(Vector2(player.abs_origin.x - 50, player.abs_origin.y - 100))
            self.screen.blit(self.amogus_right if player.side else self.amogus_left, w2s.to_pg())

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
                self.clock.tick(60)
            except KeyboardInterrupt:
                pass

    def show_menu(self):
        self.visible_group = self.menu_group

    def show_account(self):
        self.visible_group = self.account_group

    def world_to_screen(self, world: Vector2):
        return Vector2(1600 / 2 + (world.x - self.camera_pos.x), 900 / 2 + (world.y - self.camera_pos.y))

    def cl_move(self):
        local_player_id = 0
        local_player = self.player_list[local_player_id]
        in_forward = keyboard.is_pressed("w") or keyboard.is_pressed("up")
        in_backward = keyboard.is_pressed("s") or keyboard.is_pressed("down")
        in_left = keyboard.is_pressed("a") or keyboard.is_pressed("left")
        in_right = keyboard.is_pressed("d") or keyboard.is_pressed("right")
        in_use = keyboard.is_pressed("e")
        in_attack = keyboard.is_pressed(0x1)

        velocity = Vector2(0, 0)

        if in_forward:
            velocity.y = -60
        if in_backward:
            velocity.y = 60
        if in_left:
            velocity.x = -60
        if in_right:
            velocity.x = 60
        velocity.clamp(60)
        origin = local_player.origin + velocity

        local_player.rect = local_player.get_collision_rect(origin)
        if not pg.sprite.collide_mask(local_player, self.collision_map):
            self.server_update(local_player.id, origin, velocity)
        else:
            self.server_update(local_player.id, local_player.origin, Vector2(0, 0))

    def server_update(self, id, origin, velocity):
        self.player_list[id].net_update(origin, velocity)

    def show_game(self):
        self.in_game = True
        self.visible_group = self.game_group



def main():
    pg.init()
    app = App()
    # connect = threading.Thread(target=Client, args=(app,))
    # connect.start()
    app.run()


if __name__ == '__main__':
    main()
