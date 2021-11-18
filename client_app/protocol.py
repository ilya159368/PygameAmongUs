import enum


class OperationsEnum(enum.IntEnum):
    mouse_click = 1
    create_room = 2
    find_rooms = 3
    join_room = 4


# FROM CLIENT


class MouseClickRequest:
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

    def __init__(self, room_name):
        self.room_name = room_name

# FROM SERVER


class ConnectRoomResponse:
    operation = OperationsEnum.create_room

    def __init__(self, port):
        self.port = port


class FindRoomsResponse:
    operation = OperationsEnum.find_rooms

    def __init__(self, rooms_list):
        self.rooms_list = rooms_list
