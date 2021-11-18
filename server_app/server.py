import socket

from room import Room
from config import Config
import threading
import pickle
from protocol import *
from utils import is_port_in_use
from thread_ import CustomThread


class Server(socket.socket):
    def __init__(self):
        super(Server, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((Config.server_ip, Config.server_port))
        self.listen(Config.server_listen)

        self.clients_list = []
        self.rooms_list = []
        self.room_port = 9001

    def listen_connections(self):
        while 1:
            conn, addr = self.accept()
            self.clients_list.append(conn)
            print(f'Connected {conn}')
            new_thread = CustomThread(target=self.recv_data, args=(conn, addr))
            new_thread.start()

    def recv_data(self, conn: socket.socket, addr):
        while 1:
            try:
                data = conn.recv(1024)
            except socket.error:
                conn.close()
                threading.currentThread().kill()
                self.clients_list.remove(conn)
                return
            if not data:
                conn.close()
                self.clients_list.remove(conn)
                break
            req = pickle.loads(data)
            # process
            if req.operation == OperationsEnum.mouse_click:
                print(req.pos_x, req.pos_y)
            elif req.operation == OperationsEnum.create_room:
                port = self.room_port
                while is_port_in_use(port):  # checking port
                    port += 1
                new_room = Room(port, req.room_name, req.max_players)
                self.rooms_list.append(new_room)  # TODO when two rooms both with 2 players
                conn.send(pickle.dumps(ConnectRoomResponse(port)))
            elif req.operation == OperationsEnum.find_rooms:
                rooms = []
                for room in sorted(self.rooms_list, key=lambda x: len(x.players_list),
                                   reverse=True)[:5]:
                    if room.available:
                        rooms.append((room.name, len(room.players_list), room.max_players))
                out = FindRoomsResponse(rooms)
                conn.send(pickle.dumps(out))
            elif req.operation == OperationsEnum.join_room:
                room = sorted(self.rooms_list, key=lambda x: x == req.room_name and x.available)[0]
                conn.send(pickle.dumps(ConnectRoomResponse(room.port)))
            print(req)


if __name__ == '__main__':
    server = Server()
    print(f'Server is running')
    server.listen_connections()
