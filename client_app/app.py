import time
import pickle
from shared_files.protocol import *
from widgets import *
from collections import deque
import keyboard
import player
import render
import pygame as pg
import threading
from client import Client

Vector2 = render.Vector2


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
        r = pickle.dumps(req)
        self.queue_to.append(r)

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

        self.size = self.width, self.height = 1600, 900
        self.player_size = (100, 120)
        self.player_speed = 60
        self.running = True
        self.signed_in = False
        self.in_game = False
        self.offline = False
        self.connecting = True
        self.token = None
        self.screen = pg.display.set_mode(self.size)
        render.init(self.size)
        self.clock = pg.time.Clock()
        self.player_list = [player.Player()]
        self.camera_pos = Vector2(0, 0)
        self.last_update_time = 0

        # CONSTANTS
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        ALPHA = pg.SRCALPHA
        FONT_DEFAULT = pg.font.SysFont('monospace', 70)
        # images
        self.bg_img = pg.image.load('images/bg.png')
        self.back_img = pg.image.load('images/back.png')
        self.account_img = pg.image.load('images/account.png')
        self.settings_img = pg.image.load('images/settings.png')
        self.about_img = pg.image.load('images/about.png')
        self.stats_img = pg.image.load('images/statistics.png')
        self.map_image = pg.image.load("images/among_map.png")
        # self.amogus_right = pg.image.load("images/amogus.png")
        # self.amogus_right = pygame.transform.smoothscale(self.amogus_right, (100, 120))
        # self.amogus_left = pygame.transform.flip(self.amogus_right, True, False)
        self.amogus_left = pg.image.load("images/amogus.png")
        self.amogus_right = pg.image.load("images/amogus.png")
        self.amogus_left = pygame.transform.smoothscale(self.amogus_left, self.player_size)
        self.amogus_right = pygame.transform.smoothscale(self.amogus_right, self.player_size)
        self.amogus_left = pygame.transform.flip(self.amogus_left, True, False)

        self.collision_map = render.CollisionMap(pg.image.load("images/among_walls.png"))
        # groups
        self.menu_group = pg.sprite.Group()
        self.account_group = pg.sprite.Group()
        self.signin_group = pg.sprite.Group()
        self.register_group = pg.sprite.Group()
        self.ui_group = pg.sprite.Group()
        self.players_group = pg.sprite.Group()
        # main menu layout
        w, h = self.size
        small_img_button_pos = (w // 32, h // 18)
        small_img_button_size = (w // 12, w // 12)
        signin_input_size = (w // 8 * 3, h // 6)
        register_input_size = (w // 8 * 3.35, h // 8)
        # menu widgets
        self.menu_btn_play = Button((w // 3, h // 2), (w // 3, h // 5), ALPHA,
                                    Text('play', full_font=FONT_DEFAULT), border_color=WHITE,
                                    width=5, border_radius=h // 5, group=self.menu_group,
                                    func=self.show_game)
        self.menu_btn_account = Button(small_img_button_pos, small_img_button_size, ALPHA,
                                       self.account_img, group=self.menu_group,
                                       func=self.show_account)
        self.menu_btn_exit = Button((w // 32 * 27, h // 18), (True, w // 12), WHITE,
                                    Text('exit', full_font=FONT_DEFAULT), group=self.menu_group,
                                    func=self.exit, border_radius=True, width=5, border_color=WHITE)
        self.menu_btn_settings = Button((w // 3, h // 4 * 3), (w // 12, w // 12), ALPHA,
                                        self.settings_img, group=self.menu_group,
                                        func=self.show_settings)
        self.menu_btn_about = Button((w // 2 - w // 24, h // 4 * 3), (w // 12, w // 12), ALPHA,
                                     self.about_img, group=self.menu_group,
                                     func=self.show_about)
        self.menu_btn_stats = Button((w // 3 * 2 - w // 12, h // 4 * 3), (w // 12, w // 12), ALPHA,
                                     self.stats_img, group=self.menu_group,
                                     func=self.show_statistics)

        self.account_btn_back = Button(small_img_button_pos, small_img_button_size, pg.SRCALPHA,
                                       self.back_img, group=(self.signin_group, self.account_group),
                                       func=self.show_menu)
        # signin widgets
        self.signin_login = LineEdit((w // 10, h // 2.9), signin_input_size, ALPHA, WHITE, width=5,
                                     placeholder='login', border_radius=True,
                                     group=self.signin_group, full_font=FONT_DEFAULT)
        self.signin_password = LineEdit((w - w // 10 - signin_input_size[0], h // 2.9),
                                        signin_input_size, ALPHA, WHITE, width=5,
                                        placeholder='password', border_radius=True,
                                        group=self.signin_group, full_font=FONT_DEFAULT)
        self.btn_signin = Button((w // 2 - w // 6, h // 6 * 4), (w // 3, h // 8), ALPHA,
                                 Text('Sign in', full_font=FONT_DEFAULT),
                                 group=self.signin_group, border_color=WHITE,
                                 func=self.signin, border_radius=h // 8, width=5)
        self.btn_show_register = Button((w // 2 - w // 6, h // 6 * 5), (w // 3, h // 8), ALPHA,
                                        Text('Register', full_font=FONT_DEFAULT, italic=True),
                                        group=self.signin_group, func=self.show_register)
        self.signin_status_label = Label((0, h // 1.925), (w, h // 8),
                                         Text('', full_font=FONT_DEFAULT, border_color=(255, 0, 0)),
                                         ALPHA, group=self.signin_group
                                         )
        # register widgets
        self.register_btn_back = Button(small_img_button_pos, small_img_button_size, ALPHA,
                                        self.back_img, group=self.register_group,
                                        func=self.show_signin)
        self.register_username = LineEdit((w // 16, h // 3), register_input_size, ALPHA, WHITE,
                                          width=5,
                                          placeholder='username', border_radius=True,
                                          group=self.register_group, full_font=FONT_DEFAULT)
        self.register_email = LineEdit((w - w // 16 - register_input_size[0], h // 3),
                                       register_input_size, ALPHA, WHITE, width=5,
                                       placeholder='email', border_radius=True,
                                       group=self.register_group, full_font=FONT_DEFAULT)
        self.register_password1 = LineEdit((w // 16, h // 2), register_input_size, ALPHA, WHITE,
                                           width=5,
                                           placeholder='password', border_radius=True,
                                           group=self.register_group, full_font=FONT_DEFAULT)
        self.register_password2 = LineEdit((w - w // 16 - register_input_size[0], h // 2),
                                           register_input_size, ALPHA, WHITE, width=5,
                                           placeholder='repeat password', border_radius=True,
                                           group=self.register_group, full_font=FONT_DEFAULT)
        self.btn_register = Button((w // 2 - w // 6, h * 0.8), (w // 3, h // 8), ALPHA,
                                   Text('Register', full_font=FONT_DEFAULT),
                                   group=self.register_group, border_color=WHITE,
                                   func=self.register, border_radius=h // 8, width=5)
        self.register_status_label = Label((0, h // 1.5), (w, h // 8),
                                           Text('', full_font=FONT_DEFAULT, border_color=(255, 0, 0)),
                                           ALPHA, group=self.register_group,
                                           )
        # account
        self.account_username = Label((w // 2 - w // 4, h // 2.7), (w // 2, h // 7),
                                      Text('Username: "..."', full_font=FONT_DEFAULT), ALPHA, WHITE,
                                      width=5, border_radius=True, group=self.account_group)
        self.account_btn_signout = Button((w // 8 * 0.75, h // 3 * 2), (w // 8 * 3, h // 8), ALPHA,
                                          Text('sign out', full_font=FONT_DEFAULT),
                                          group=self.account_group, border_color=WHITE,
                                          func=self.signout, border_radius=h // 8, width=5)
        self.account_btn_change = Button((w // 8 * 4.25, h // 3 * 2), (w // 8 * 3, h // 8), ALPHA,
                                         Text('change name', full_font=FONT_DEFAULT),
                                         group=self.account_group, border_color=WHITE,
                                         func=self.change_name, border_radius=h // 8, width=5)
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
            if time.time() - self.last_update_time > 1 / 16:
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
        while self.running:
            self.update()
            # events / send
            e: pg.event.Event
            for e in pg.event.get():
                # system
                if e.type == pg.QUIT:
                    [func() for func in self.before_exit]
                    self.running = False
                elif e.type in (pg.WINDOWRESIZED, pg.WINDOWSHOWN):
                    self.resize_event()
                # gameplay
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
                # тут писал криворукий
                elif resp.operation == 'register':
                    if resp.kwargs['status'] == 'ok':
                        self.show_signin()
                    else:
                        self.register_status_label.text.set_text(resp.kwargs['status'])

                elif resp.operation == 'sign_in':
                    if resp.kwargs['status'] == 'ok':
                        self.signed_in = True
                        self.show_menu()
                    else:
                        self.signin_status_label.text.set_text(resp.kwargs['status'])
            self.draw()
            try:
                pg.display.flip()
                self.clock.tick(60)
            except KeyboardInterrupt:
                pass
        pg.quit()

    def world_to_screen(self, world: Vector2):
        return Vector2(self.width / 2 + (world.x - self.camera_pos.x),
                       self.height / 2 + (world.y - self.camera_pos.y))

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
            velocity.y = -self.player_speed
        if in_backward:
            velocity.y = self.player_speed
        if in_left:
            velocity.x = -self.player_speed
        if in_right:
            velocity.x = self.player_speed
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
        if self.signed_in:
            self.in_game = True
            self.visible_group = self.players_group
        else:
            self.show_signin()

    def show_menu(self):
        self.visible_group = self.menu_group

    def show_signin(self):  # TODO: clear fields if reopen; fill fields if registered;
        self.visible_group = self.signin_group

    def show_account(self):
        if self.signed_in:
            self.visible_group = self.account_group
        else:
            self.show_signin()

    def show_register(self):
        self.visible_group = self.register_group

    def exit(self):
        self.running = False

    def signin(self):
        if self.signin_login.text and self.signin_password.text:
            self.to_queue(Token(
                'sign_in', name=self.signin_login.text, password=self.signin_password.text
            ))

    def register(self):
        # проверка на пустые строки и разные пароли
        if self.register_password1.text == self.register_password1.text and self.register_password1 and \
                self.register_email.text and self.register_username.text:
            self.to_queue(Token(
                'register', name=self.register_username.text, password=self.register_password1.text,
                email=self.register_email.text
            ))

    def show_settings(self):
        ...

    def show_statistics(self):
        ...

    def show_about(self):
        ...

    def signout(self):
        self.signed_in = False
        self.visible_group = self.menu_group

    def change_name(self):
        ...


def main():
    pg.init()
    app = App()
    connect = threading.Thread(target=Client, args=(app,))
    connect.start()
    app.run()


if __name__ == '__main__':
    main()
