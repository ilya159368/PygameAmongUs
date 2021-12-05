from player import Player, Vector2
import keyboard
import server


__camera_position = Vector2(0, 0)


def get_camera_pos():
    return __camera_position


def world_to_screen(origin):
    relative = __camera_position - globals.screen_resolution / 2
    return origin - relative


def get_local_player_id():
    return 0


def cl_move():
    in_forward = keyboard.is_pressed("w") or keyboard.is_pressed("up")
    in_backward = keyboard.is_pressed("s") or keyboard.is_pressed("down")
    in_left = keyboard.is_pressed("a") or keyboard.is_pressed("left")
    in_right = keyboard.is_pressed("d") or keyboard.is_pressed("right")
    in_use = keyboard.is_pressed("e")
    in_attack = keyboard.is_pressed("mouse1")
    owner_id = get_local_player_id()