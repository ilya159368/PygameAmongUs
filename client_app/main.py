import math
import pickle
import time

from task import *

from protocol import *
from widgets import *
from collections import deque
from player import *
import render
import pygame as pg
import threading
from client import Client

from auto_reg import *
from timer import Timer, ProgressBar

from MY_TEST import VotingList, TaskList

Vector2 = render.Vector2


class App:
    # service funcs ------------------
    def add_before_exit(self, func):
        self.before_exit.append(func)

    def to_queue(self, req):
        if self.offline or self.connecting:
            return
        req.in_game = self.in_game
        r = pickle.dumps(req)
        print(len(r), 'send')
        self.queue_to.append(r)
        if self.send_thread.is_paused():
            self.send_thread.resume()

    def from_queue(self):
        if self.offline:
            return
        a: bytes = self.queue_from.popleft()
        print(len(a), 'recv')
        return pickle.loads(a)

    # end service funcs --------------

    def __vg_getter(self):
        return self._visible_group

    def __vg_setter(self, vg):
        if hasattr(self, '_visible_group'):
            self._visible_group: pg.sprite.Group
            for sprite in self._visible_group.sprites():
                if type(sprite) in (Label, LineEdit):
                    sprite.set_default()
        self._visible_group = vg

    visible_group = property(__vg_getter, __vg_setter)

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
        self.name = ""
        self.offline = False
        self.connecting = True
        self.token = None
        pg.display.set_caption("Pymogus")
        pg.display.set_icon(pg.image.load('images/ico.png'))
        self.screen = pg.display.set_mode(self.size)
        render.init(self.size)
        self.clock = pg.time.Clock()
        self.player_list = [Player(), Player()]
        self.id = 0  # for test
        self.camera_pos = Vector2(0, 0)
        self.last_update_time = 0
        self.is_host = False
        self.tasks_dict = {WiresTask: (
            (5235, 2400), (4640, 2814), (3596, 2629), (4035, 303), (2182, 2078), (7600, 1982)),
            NumbersTask: ((928, 1685),), VotingList: ((4675, 1120),),
            GarbageTask: ((4910, 4170), (5523, 528),),
            SendEnergy: ((3364, 2558),),
            ReceiveEnergy: ((1380, 1810), (1883, 679), (1742, 2909), (7043, 874),
                            (6496, 1695), (7870, 1689), (6918, 3070), (6097, 3782))}
        self.task_widget = None
        self.vents_list = [((5749, 1307), (6671, 2416), (5440, 3045)), ((6575, 660), (7865, 1833)), ((7866, 2408), (6700, 3836)),
                           ((2729, 2508), (3076, 2007), (3222, 2707)), ((2238, 3717), (1239, 2512)), ((1044, 1804), (2230, 806))]
        self.active_object = None
        self.can_move = True
        self.in_vent = False
        self.active_vent_group = None
        self.tasks_to_make = []
        self.add_before_exit(self.delete_room)
        self.update_screen = True

        # CONSTANTS
        self.task_bar = None
        # images
        self.bg_img = pg.image.load('images/bg.png')
        self.back_img = pg.image.load('images/back.png')
        self.account_img = pg.image.load('images/account.png')
        self.settings_img = pg.image.load('images/settings.png')
        self.about_img = pg.image.load('images/about.png')
        self.create_img = pg.image.load('images/create.png')
        self.refresh_img = pg.image.load('images/refresh.png').convert_alpha()
        self.close_img = pg.image.load('images/close.png').convert_alpha()
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
        self.bg_ejected = pg.image.load('images/ejected.png')

        self.kill_sound = pg.mixer.Sound("sound/imposter_kill.mp3")
        self.death_sound = pg.mixer.Sound("sound/death.mp3")
        self.report_sound = pg.mixer.Sound("sound/report.mp3")
        self.step_sound = pg.mixer.Sound("sound/steps.mp3")

        self.last_step_sound = 0

        self.collision_map = render.CollisionMap(pg.image.load("images/among_walls.png"))
        # groups
        self.menu_group = pg.sprite.Group()
        self.account_group = pg.sprite.Group()
        self.signin_group = pg.sprite.Group()
        self.register_group = pg.sprite.Group()
        self.find_group = pg.sprite.Group()
        self.create_group = pg.sprite.Group()
        self.wait_group = pg.sprite.Group()
        self.ui_group = pg.sprite.Group()
        self.pause_menu_group = pg.sprite.Group()
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
                                    func=self.show_find)
        self.menu_btn_account = Button(small_img_button_pos, small_img_button_size, ALPHA,
                                       self.account_img, group=self.menu_group,
                                       func=self.show_account)
        self.menu_btn_exit = Button((w // 32 * 27, h // 18), (True, w // 12), ALPHA,
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

        self.btn_back = Button(small_img_button_pos, small_img_button_size, pg.SRCALPHA,
                               self.back_img,
                               group=(self.signin_group, self.account_group, self.find_group),
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
                                         Text('', full_font=FONT_DEFAULT, color=(255, 0, 0)),
                                         ALPHA, group=self.signin_group)
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
                                           Text('', full_font=FONT_DEFAULT, color=(255, 0, 0)),
                                           ALPHA, group=self.register_group,
                                           )
        # account
        self.account_username = Label((w // 2 - w // 4, h // 2.7), (w // 2, h // 7),
                                      Text(f'Username: "{self.name}"', full_font=FONT_DEFAULT),
                                      ALPHA, WHITE,
                                      width=5, border_radius=True, group=self.account_group)
        self.account_btn_signout = Button((w // 8 * 0.75, h // 3 * 2), (w // 8 * 3, h // 8), ALPHA,
                                          Text('sign out', full_font=FONT_DEFAULT),
                                          group=self.account_group, border_color=WHITE,
                                          func=self.signout, border_radius=h // 8, width=5)
        self.account_btn_change = Button((w // 8 * 4.25, h // 3 * 2), (w // 8 * 3, h // 8), ALPHA,
                                         Text('change name', full_font=FONT_DEFAULT),
                                         group=self.account_group, border_color=WHITE,
                                         func=self.change_name, border_radius=h // 8, width=5)
        # find rooms
        self.btn_refresh = Button((w // 6 * 5.05, h // 3 * 0.9),
                                  (w // 10, h // 10), ALPHA, self.refresh_img,
                                  func=self.find, group=self.find_group)
        self.find_list = ListWidget((w // 6, h // 3), (w * 2 // 3, h // 2), ALPHA,
                                    group=self.find_group,
                                    border_color=WHITE, width=5, border_radius=h // 14)
        self.btn_show_create = Button((w - w // 32 - small_img_button_size[0], h // 18),
                                      small_img_button_size, ALPHA, self.create_img,
                                      func=self.show_create, args=(), group=self.find_group)
        self.find_status_label = Label((0, h - h // 7), (w, h // 8),
                                       Text('', full_font=FONT_DEFAULT, color=WHITE, italic=True),
                                       ALPHA, group=self.find_group)
        # create
        self.btn_create_back = Button(small_img_button_pos, small_img_button_size, pg.SRCALPHA,
                                      self.back_img,
                                      group=self.create_group,
                                      func=self.create_back)
        self.create_title = LineEdit((w // 10, h // 2.5), (w // 8 * 4, h // 6), ALPHA, WHITE,
                                     width=5,
                                     placeholder='title', border_radius=True,
                                     group=self.create_group, full_font=FONT_DEFAULT)
        self.create_max = LineEdit((w // 10 * 7, h // 2.5), (w // 8 * 2, h // 6), ALPHA, WHITE,
                                   width=5,
                                   placeholder='max/10', border_radius=h // 12,
                                   group=self.create_group, full_font=FONT_DEFAULT)
        self.btn_create = Button((w // 2 - w // 6, h // 6 * 4.5), (w // 3, h // 8), ALPHA,
                                 Text('Create', full_font=FONT_DEFAULT),
                                 group=self.create_group, border_color=WHITE,
                                 func=self.create, border_radius=h // 8, width=5)
        self.create_status_label = Label((0, h // 1.65), (w, h // 8),
                                         Text('', full_font=FONT_DEFAULT, color=(255, 0, 0)),
                                         ALPHA, group=self.create_group)
        # waiting
        self.btn_wait_close = Button((w - w // 32 - small_img_button_size[0], h // 18),
                                     small_img_button_size, pg.SRCALPHA,
                                     self.close_img,
                                     group=self.wait_group,
                                     func=self.wait_close)
        self.wait_label = Label((w // 3, h // 2 - h // 16), (w // 3, h // 8),
                                Text('1/10', full_font=FONT_BIG, color=WHITE),
                                ALPHA, group=self.wait_group)

        # pause menu
        self.play_button = Button((w * 0.25, h // 2), (w // 2, h // 5), ALPHA,
                                  Text('continue', full_font=FONT_DEFAULT), border_color=WHITE,
                                  width=5, border_radius=h // 5, group=self.pause_menu_group,
                                  func=self.close_settings)

        self.pause_menu_btn_exit = Button((w * 0.4, h * 0.8), (w * 0.2, w // 12), ALPHA,
                                          Text('exit', full_font=FONT_DEFAULT),
                                          group=self.pause_menu_group,
                                          func=self.exit, border_radius=h // 5, width=5,
                                          border_color=WHITE)

        self.volume_slider = SliderInt("Volume", (w // 2 - 250, h // 4), 0, 100, self.screen,
                                       FONT_DEFAULT)
        # ui
        self.close_task_btn = Button(
            (self.width - self.height // 10 - self.height // 20, self.height // 20),
            (self.height // 10, self.height // 10),
            pg.SRCALPHA, self.close_img,
            func=self.close_task, hovered_color=(120, 120, 120))

        # PREDEFINE
        self.visible_group = self.menu_group

    def resize_event(self):
        self.bg_img = pg.transform.smoothscale(self.bg_img, self.screen.get_size())
        self.bg_ejected = pg.transform.smoothscale(self.bg_ejected, self.screen.get_size())

    def draw(self):
        if self.in_game:
            self.screen.fill((0, 0, 0))
            if self.visible_group is not self.pause_menu_group:
                self.screen.blit(self.map_image,
                                 self.world_to_screen(Vector2(0, 0)).to_pg())  # TODO blit once ?
            if time.time() - self.last_update_time > 1 / 16:
                self.cl_move()
                self.last_update_time = time.time()
            if self.can_move:
                self.player_list[self.id].frame_update()
            if not self.in_vent:
                self.camera_pos = self.player_list[self.id].abs_origin
            if self.visible_group is not self.pause_menu_group:
                self.draw_players()
            if self.player_list[self.id].imposter and time.time() - self.imposter_cooldown < 30:
                text = FONT_BOLD.render(str(30 - int(time.time() - self.imposter_cooldown)), True,
                                        Color((255, 0, 0)))
                self.screen.blit(text,
                                 (self.width - text.get_width(), self.height - text.get_height()))
        else:
            if self.visible_group is self.pause_menu_group:
                self.screen.blit(self.bg_ejected, (0, 0))
            else:
                self.screen.blit(self.bg_img, (0, 0))
            # self.screen.fill((255, 0, 0))
        [self.screen.blit(s.image, s.rect, special_flags=pg.BLEND_RGBA_ADD) for s in
         self.visible_group.sprites()]
        if self.visible_group is self.pause_menu_group:
            self.volume_slider.draw()
        if self.active_object:
            self.active_object.draw()
        if self.in_vent:
            temp = pg.Surface(self.size)
            temp.fill(pg.Color(0, 0, 0))
            temp.set_alpha(100)
            self.screen.blit(temp, (0, 0))
        if self.in_game and self.task_bar is not None:
            self.task_bar.draw()
        if self.in_game and self.task_widget is not None:
            self.task_widget.draw()
        # self.timer.draw()

    def update(self):
        self.visible_group.update()
        if self.active_object is not None:
            self.active_object.update()

        if self.visible_group is self.pause_menu_group:
            self.volume_slider.update()

    def draw_players(self):
        for player in self.player_list:
            if not player.show:
                continue
            if player != self.player_list[self.id]:
                player.frame_update()
            w2s = self.world_to_screen(Vector2(player.abs_origin.x - 50, player.abs_origin.y - 100))
            if player == self.player_list[self.id] and self.in_vent:
                continue
            self.screen.blit(player.get_image(), w2s.to_pg())
            if player.alive:
                rfont = FONT_DEFAULT.render(player.name, False,
                                            WHITE if not player.imposter else (255, 0, 0))
                self.screen.blit(rfont,
                                 (w2s.x - rfont.get_width() / 2 + 50, w2s.y - 100))

    def run(self):
        while self.running:
            self.update()
            # events / send ---------
            e: pg.event.Event
            for e in pg.event.get():
                # system
                if e.type == pg.QUIT:
                    self.exit()
                elif e.type in (pg.WINDOWRESIZED, pg.WINDOWSHOWN):
                    self.resize_event()
                # gameplay
                # elif e.type == pg.KEYDOWN and e.key == pg.K_c and not self.in_game:
                #     self.to_queue(Token('create', name='name', max=2))
                # elif e.type == pg.KEYDOWN and e.key == pg.K_f:
                #     self.to_queue(Token('find'))
                elif e.type == pg.KEYDOWN and e.key == pg.K_j:
                    self.to_queue(
                        Token('join', token=self.token))  # TODO: room = None when restart !!!
                elif self.in_vent and e.type == pg.KEYDOWN and e.key == pg.K_e:
                    self.exit_vent()
                elif e.type == pg.KEYDOWN and e.key == pg.K_e:
                    # расстояние от центра задания до центра игрока <= дальности взаимодействия
                    player = self.player_list[self.id]
                    pl_center = player.origin - Vector2(0, 60)
                    if player.imposter:
                        for tup in self.vents_list:
                            for center in tup:
                                if math.sqrt(abs(center[0] - pl_center.x) ** 2 + abs(
                                        center[1] - pl_center.y) ** 2) <= player.interact_range:
                                    self.active_vent_group = tup
                                    self.show_vent(center)
                                    self.can_move = False
                    elif player.alive:
                        for cls, tup in self.tasks_dict.items():
                            for center in tup:
                                if ((
                                        Vector2(
                                            *center) - pl_center).length() <= player.interact_range and
                                        center in [t[1] for t in self.tasks_to_make] or (
                                                (Vector2(
                                                    *center) - pl_center).length() <= 450 and cls is VotingList)):  # для
                                    # радиуса стола
                                    if cls is NumbersTask:
                                        self.active_object = cls(self.width // 10, self.height // 6,
                                                                 self.height // 6 * 4 // 5,
                                                                 self.screen,
                                                                 FONT_DEFAULT,
                                                                 callback=self.close_task,
                                                                 world_pos=center)
                                        self.ui_group.add(self.close_task_btn)
                                    elif cls is VotingList:
                                        self.to_queue(Token('voting'))
                                    else:
                                        self.active_object = cls(
                                            (self.width // 10, self.height // 6),
                                            (self.width // 10 * 8,
                                             self.height // 6 * 4),
                                            self.screen, callback=self.close_task, world_pos=center)
                                        self.ui_group.add(self.close_task_btn)
                                    self.can_move = False
                elif self.in_vent and e.type == pg.KEYDOWN and e.key == pg.K_LEFT:
                    self.start_vent -= 1
                    if self.start_vent < 0:
                        self.start_vent = len(self.active_vent_group) - 1
                    self.camera_pos = Vector2(*self.active_vent_group[self.start_vent])
                elif self.in_vent and e.type == pg.KEYDOWN and e.key == pg.K_RIGHT:
                    self.start_vent += 1
                    if self.start_vent > len(self.active_vent_group) - 1:
                        self.start_vent = 0
                    self.camera_pos = Vector2(*self.active_vent_group[self.start_vent])
                elif e.type == pg.KEYDOWN and e.key == pg.K_q:
                    local_player = self.player_list[self.id]
                    if not local_player.imposter or time.time() - self.imposter_cooldown < 30.0 or not local_player.alive:
                        continue
                    nearest_player = 0
                    nearest_dist = 1000
                    for i in range(len(self.player_list)):
                        if i == self.id:
                            continue
                        player = self.player_list[i]
                        if not player.alive:
                            continue
                        dist = (player.origin - local_player.origin).length()
                        if dist < nearest_dist:
                            nearest_dist = dist
                            nearest_player = i
                    if nearest_dist < local_player.interact_range:
                        # self.player_list[nearest_player].alive = False
                        self.to_queue(Token('kill', dead=self.player_list[nearest_player].name))
                        self.imposter_cooldown = time.time()
                        self.kill_sound.set_volume(self.volume_slider.value / 100)
                        self.kill_sound.play()
                        # тут килляем игрока на сервере с айди nearest_player

                elif e.type == pg.KEYDOWN and e.key == pg.K_f:
                    local_player = self.player_list[self.id]
                    if not local_player.alive:
                        continue
                    for i in range(len(self.player_list)):
                        if i == self.id:
                            continue
                        player = self.player_list[i]
                        if player.alive:
                            continue
                        dist = (player.origin - local_player.origin).length()
                        if dist < local_player.interact_range:
                            self.to_queue(Token('voting'))
                            # тут отправляем инфу на сервер, кто зарепортил(айди) и кого зарепортил (айди)
                            self.report_sound.set_volume(self.volume_slider.value / 100)
                            self.report_sound.play()
                elif e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE and self.in_game:
                    self.visible_group = self.pause_menu_group
                if self.visible_group is self.pause_menu_group:
                    self.volume_slider.handle_events(e)

            # move to server
            if self.in_game and not self.offline and not self.active_object and self.player_list[
                self.id].alive:
                player: Player = self.player_list[self.id]
                self.to_queue(
                    Token('move', id=self.id, origin=player.origin, velocity=player.velocity))

            # drawing / recv ---------
            if self.queue_from:
                if self.in_game:
                    # print(len(self.queue_from))
                    # for i in self.queue_from:
                    #     if i.operation == 'voting':
                    #         print('______________voting in queue________________')
                    for _ in range(len(self.queue_from)):
                        try:
                            if len(self.queue_from):
                                resp = self.from_queue()
                                if resp.operation != 'move':
                                    print(resp.operation)
                                if resp.operation == 'move':
                                    self.player_list[resp.kwargs['id']].net_update(
                                        resp.kwargs['origin'],
                                        resp.kwargs['velocity'])
                                    if self.player_list[resp.kwargs[
                                        "id"]].velocity.length_sqr() > 1 and time.time() - self.last_step_sound > 0.9:
                                        self.last_step_sound = time.time()
                                        self.step_sound.set_volume(self.volume_slider.value / 100)
                                        self.step_sound.stop()
                                        self.step_sound.play()

                                elif resp.operation == 'voting':
                                    print('___________________voting________________')
                                    self.show_voting()
                                    self.task_bar.completed = resp.kwargs['task_complete']
                                elif resp.operation == 'kill':
                                    self.player_list[[pl.name for pl in self.player_list].index(
                                        resp.kwargs['dead'])].disable()
                                    if [pl.name for pl in self.player_list].index(
                                            resp.kwargs['dead']) == self.id:
                                        self.can_move = False
                                        self.death_sound.set_volume(self.volume_slider.value / 100)
                                        self.death_sound.play()
                                elif resp.operation == 'end_voting':
                                    id_ = resp.kwargs['voted']
                                    if id_ is not None:
                                        self.player_list[id_].show = False
                                        self.player_list[id_].alive = False
                                    self.show_ejected(id_)
                                    threading.Timer(5, self.close_voting).start()
                                elif resp.operation == 'make_voted':
                                    self.active_object.make_voted(resp.kwargs['id_'])
                        except Exception as e:
                            print('lost|empty queue', e)
                    # print(len(self.queue_from))
                else:
                    resp = self.from_queue()
                    if resp.operation == 'find':
                        rooms = resp.kwargs['rooms']
                        # [rooms.extend(rooms) for _ in range(4)]
                        buttons = []
                        for i, r in enumerate(rooms):
                            spaces = 21 - len(r[0] + str(r[1]) + str(r[2])) - 2
                            if spaces < 0:
                                r[0] = r[0][:spaces - 5] + '...'
                                spaces = 2
                            text = r[0] + ' ' * spaces + f"{r[1]}/{r[2]}"
                            btn = Button((0, 0), (0, 0), GRAY,
                                         Text(text, full_font=FONT_BOLD, color=BLUEBLACK),
                                         self.join(r[3]), border_radius=True)  # замыкание
                            btn.token = r[3]
                            buttons.append(btn)
                        self.find_list.extend(buttons)
                        if self.show_find_status:
                            self.find_status_label.set_text('refreshed')
                            timer = threading.Timer(3.0, lambda: self.find_status_label.set_text(''))
                            timer.start()
                        print(rooms)
                    elif resp.operation == 'init':
                        temp_list = []
                        self.task_bar = ProgressBar((10, 10), (self.width // 3, 50), self.screen,
                                                    len(resp.kwargs['players']) * 7)
                        for i, (name, color, imposter) in enumerate(resp.kwargs['players']):
                            pl = Player()
                            pl.color = color
                            pl.name = name
                            pl.imposter = True
                            pl.id = i
                            pl.load_anims()
                            pl.set_meet_point()
                            temp_list.append(pl)
                        self.player_list = temp_list
                        self.tasks_to_make = resp.kwargs['tasks'][self.id]
                        print([t[1] for t in self.tasks_to_make])
                        self.task_widget = TaskList((10, 60), (310, 175), self.tasks_to_make,
                                                    self.screen)
                        self.show_game()
                    elif resp.operation == 'join':
                        if resp.kwargs['status'] == 'bad':
                            self.create_status_label.set_text('room is not available')
                            self.find()  # refresh
                        else:
                            self.id = resp.kwargs['id']
                            self.token = resp.kwargs['token']
                            self.show_wait()
                            self.wait_label.set_text(f'{resp.kwargs["cnt"]}/{resp.kwargs["max_"]}')
                        print(self.id)
                    elif resp.operation == 'create':
                        if resp.kwargs['status'] == 'bad':
                            self.create_status_label.set_text('name is already taken')
                        else:
                            self.id = resp.kwargs['id']
                            self.token = resp.kwargs['token']
                            self.is_host = True
                            self.show_wait()
                            self.wait_label.set_text(f'1/{self.room_max}')
                        print(self.id, 'ok')
                    elif resp.operation == 'connected':
                        self.wait_label.set_text(f'{resp.kwargs["cnt"]}/{resp.kwargs["max_"]}')
                    elif resp.operation == 'quit':
                        self.show_find()
                        ...
                    # тут писал криворукий
                    elif resp.operation == 'register':
                        if resp.kwargs['status'] == 'ok':
                            self.show_signin()
                        else:
                            self.register_status_label.set_text(resp.kwargs['status'])
                    elif resp.operation == 'sign_in':
                        if resp.kwargs['status'] == 'ok':
                            self.signed_in = True
                            self.name = resp.kwargs['my_name']
                            self.account_username.set_text(resp.kwargs['my_name'])
                            if self.visible_group is self.menu_group:
                                self.show_find()
                            else:
                                self.show_menu()
                        else:
                            self.visible_group = self.signin_group
                            self.signin_status_label.set_text(resp.kwargs['status'])
            self.draw()  # TODO fix cpu usage
            try:
                if self.update_screen:
                    pg.display.flip()
                self.clock.tick(32)
            except KeyboardInterrupt:
                pass
        pg.quit()
        exit()

    def show_vent(self, center):
        self.in_vent = True
        self.start_vent = self.active_vent_group.index(center)

    def exit_vent(self):
        self.in_vent = False
        self.player_list[self.id].origin = Vector2(*self.active_vent_group[self.start_vent])
        self.start_vent = None
        self.active_vent_group = None
        self.can_move = True

    def world_to_screen(self, world: Vector2):
        return Vector2(self.width / 2 + (world.x - self.camera_pos.x),
                       self.height / 2 + (world.y - self.camera_pos.y))

    def cl_move(self):
        if not self.can_move:
            return
        local_player_id = self.id
        local_player = self.player_list[local_player_id]
        keys = pg.key.get_pressed()
        in_forward = keys[pg.K_w] or keys[pg.K_UP]
        in_backward = keys[pg.K_s] or keys[pg.K_DOWN]
        in_left = keys[pg.K_a] or keys[pg.K_LEFT]
        in_right = keys[pg.K_d] or keys[pg.K_RIGHT]

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
            self.server_update(local_player_id, origin, velocity)
        else:
            self.server_update(local_player_id, local_player.origin, Vector2(0, 0))

        if velocity.length_sqr() > 1 and time.time() - self.last_step_sound > 0.9:
            self.last_step_sound = time.time()
            self.step_sound.set_volume(self.volume_slider.value / 100)
            self.step_sound.stop()
            self.step_sound.play()

    def server_update(self, id, origin, velocity):
        self.player_list[id].net_update(origin, velocity)

    def show_game(self):
        self.in_game = True
        self.visible_group = self.ui_group
        self.imposter_cooldown = time.time()

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
        for func in self.before_exit:
            func()
        self.running = False

        winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Pymogus")
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Pymogus", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "volume", 0, winreg.REG_SZ, str(self.volume_slider.value))
        winreg.CloseKey(key)

    def signin(self):
        if self.signin_login.text and self.signin_password.text:
            self.to_queue(Token(
                'sign_in', name=self.signin_login.text, password=self.signin_password.text
            ))
            save_account(self.signin_login.text, self.signin_password.text)

    def send_(self, id_):
        self.to_queue(Token('vote', choice_=id_))

    def register(self):
        # проверка на пустые строки и разные пароли
        if self.register_password1.text == self.register_password1.text and self.register_password1 and \
                self.register_email.text and self.register_username.text:
            self.to_queue(Token(
                'register', name=self.register_username.text, password=self.register_password1.text,
                email=self.register_email.text
            ))

    def show_settings(self):
        self.visible_group = self.pause_menu_group

    def close_settings(self):
        if self.in_game:
            self.visible_group = self.ui_group
        else:
            self.visible_group = self.menu_group

    def show_statistics(self):
        ...

    def show_about(self):
        ...

    def signout(self):
        self.signed_in = False
        self.visible_group = self.menu_group

    def change_name(self):
        ...

    def find(self):
        self.show_find_status = True
        self.find_list.set([])
        self.to_queue(Token('find'))

    def show_find(self):
        self.find()
        self.show_find_status = False
        acc = load_account()
        if self.signed_in:
            self.visible_group = self.find_group
        elif acc[0]:
            self.to_queue(Token(
                'sign_in', name=acc[1], password=acc[2]))
        else:
            self.show_signin()

    def show_create(self):
        self.visible_group = self.create_group

    def join(self, token):
        def _send():
            self.room = token
            self.to_queue(Token('join', token=token))

        return _send

    def create(self):
        try:
            max_ = int(self.create_max.text)
        except ValueError:
            self.create_status_label.set_text('max must be number')
            return
        # if not 5 <= max_ <= 10:
        #     self.create_status_label.set_text('incorrect max players (from 5 till 10)')
        #     return
        if self.create_status_label.text:
            self.create_status_label.set_text('')
        self.to_queue(Token('create', name=self.create_title.text,
                            max=max_))
        self.room_max = max_

    def create_back(self):
        # self.to_queue(Token('delete', token=self.token))
        self.visible_group = self.find_group

    def wait_close(self):
        self.delete_room()
        if self.is_host:
            self.visible_group = self.create_group
        else:
            self.visible_group = self.find_group

    def show_wait(self):
        self.visible_group = self.wait_group

    def delete_room(self):
        if self.token:
            if self.is_host:
                self.to_queue(Token('delete', token=self.token))
                self.is_host = False
            else:
                self.to_queue(Token('quit'))
            time.sleep(0.3)  # TODO fix maybe
        else:
            print('delete: empty token')

    def show_voting(self):
        self.active_object = VotingList(
            (self.width // 2 - 854 // 2, self.height // 2 - 577 // 2), (854, 577),
            self.player_list, self.screen,
            self.player_list[self.id].imposter, self.send_,
            self.player_list[self.id].alive)
        self.active_object.alive = self.player_list[self.id].alive
        [pl.set_meet_point() for pl in self.player_list if pl.alive]
        for pl in self.player_list:
            self.camera_pos = Vector2(4832 + math.cos(pl.id * 36) * 300,
                                      1080 + math.sin(pl.id * 36) * 300)
        self.can_move = False  # TODO fix bcz update after disable

    def close_task(self, done=0, task=None):
        self.active_object = None
        self.can_move = True
        if self.ui_group.has(self.close_task_btn):
            self.ui_group.remove(self.close_task_btn)
        if done:
            self.task_widget.visual_tasks[
                [t.task_name for t in self.task_widget.visual_tasks].index(task)].status = True

            self.to_queue(Token('task'))

    def close_voting(self):
        self.active_object = None
        self.can_move = True
        for pl in self.player_list:
            if not pl.alive:
                pl.show = False
        self.update_screen = True

    def show_ejected(self, id):
        self.screen.blit(self.bg_ejected, (0, 0))
        if id is None:
            text = 'No one was ejected...'
        else:
            text = f'{self.player_list[id].name.capitalize()} was ejected...'
        label = Label((0, self.height // 2 - self.height // 10), (self.width, self.height // 5),
                      Text(text, full_font=FONT_BOLD), ALPHA)
        self.screen.blit(label.image, label.rect)
        pg.display.flip()
        self.update_screen = False


def main():
    app = App()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Pymogus", 0, winreg.KEY_READ)
        app.volume_slider.value = float(winreg.QueryValueEx(key, "volume")[0])
        winreg.CloseKey(key)
    except OSError:
        app.volume_slider.value = 50
    connect = threading.Thread(target=Client, args=(app,))
    connect.start()
    app.run()


if __name__ == '__main__':
    pg.init()
    WHITE = (255, 255, 255)
    GRAY = (224, 224, 224)
    BLACK = (0, 0, 0)
    BLUEBLACK = (39, 39, 39)
    ALPHA = pg.SRCALPHA
    FONT_DEFAULT = pg.font.SysFont('monospace', 70)
    FONT_BIG = pg.font.SysFont('monospace', 120, bold=True)
    FONT_BOLD = pg.font.SysFont('monospace', 70, bold=True)
    main()
