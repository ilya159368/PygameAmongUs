import enum


class OperationsEnum(enum.IntEnum):
    mouse_click = 1
    create_room = 2
    find_rooms = 3
    join_room = 4
    move = 5


# FROM CLIENT

class MouseClickRequest:
    operation = OperationsEnum.mouse_click

    def __init__(self, pos_x, pos_y):
        self.pos_x, self.pos_y = pos_x, pos_y


class MouseClickRoomRequest:
    operation = OperationsEnum.mouse_click

    def __init__(self, pos_x, pos_y):
        self.pos_x, self.pos_y = pos_x, pos_y


class CreateRoomRequest:
    operation = OperationsEnum.create_room

    def __init__(self, room_name, max_players):
        self.room_name, self.max_players = room_name, max_players


class FindRoomsRequest:
    operation = OperationsEnum.find_rooms


class JoinRoomRequest:
    operation = OperationsEnum.join_room

    def __init__(self, token):
        self.token = token


class MoveRequest:
    operation = OperationsEnum.move

    def __init__(self, origin, alive, imposter, color):
        pass


# FROM SERVER


class RoomTokenResponse:
    operation = OperationsEnum.create_room

    def __init__(self, token):
        self.token = token


class FindRoomsResponse:
    """every room is represented as (room.name, len(room.players_list), room.max_players, room.token)"""
    operation = OperationsEnum.find_rooms

    def __init__(self, rooms_list):
        self.rooms_list = rooms_list


class JoinRoomResponse:
    operation = OperationsEnum.create_room

    def __init__(self, id):
        self.id = id


class Token:
    def __init__(self, operation, **kwargs):
        self.in_game = None
        self.operation = operation
        self.kwargs = kwargs


class DeepToken:
    def __init__(self, operation, **kwargs):
        self.operation = operation
        for k, v in kwargs.items():
            self.__setattr__(k, v)
