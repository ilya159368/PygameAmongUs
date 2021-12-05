import socket

from room import Room
from config import Config
import threading
import pickle
from shared_files.protocol import *
from shared_files.thread_ import CustomThread
from client import Client

class Server(socket.socket):
    def __init__(self):
        super(Server, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((Config.server_ip, Config.server_port))
        self.listen(Config.server_listen)

        self.clients_list = []
        self.rooms_list = []
        self.room_token = 111

    def listen_connections(self):
        while 1:
            conn, addr = self.accept()
            self.clients_list.append(Client(conn))
            print(f'Connected {conn}')
            new_thread = CustomThread(target=self.recv_data, args=(conn, addr))
            new_thread.start()

    def recv_data(self, conn: socket.socket, addr):
        client = sorted(self.clients_list, key=lambda x: x.conn is conn, reverse=True)[0]
        while 1:
            try:
                data = conn.recv(1024)
            except socket.error:
                conn.close()
                self.clients_list.remove(conn)
                client.room.delete_client(client)
                threading.currentThread().kill()
                return
            if not data:
                conn.close()
                self.clients_list.remove(conn)
                client.room.delete_client(client)
                threading.currentThread().kill()
                return

            req = pickle.loads(data)
            # process game
            if req.in_game:
                if req.operation == OperationsEnum.move:
                    for client_el in client.room.players_list:
                        if client_el is not client:
                            client_el.queue.append(req)
                            client_el.send_thread.resume()
            else:
                # process menu
                if req.operation == OperationsEnum.mouse_click:
                    print(req.pos_x, req.pos_y)
                elif req.operation == OperationsEnum.create_room:
                    token = self.room_token
                    room = Room(token, req.room_name, req.max_players)
                    self.room_token += 1
                    self.rooms_list.append(room)  # TODO when two rooms both with 2 players
                    client.room = room
                    room.players_list.append(client)
                    conn.send(pickle.dumps(RoomTokenResponse(token)))
                elif req.operation == OperationsEnum.find_rooms:
                    rooms = []
                    for room in sorted(self.rooms_list, key=lambda x: len(x.players_list),
                                       reverse=True)[:5]:
                        if room.available:
                            rooms.append((room.name, len(room.players_list), room.max_players, room.token))
                    out = FindRoomsResponse(rooms)
                    conn.send(pickle.dumps(out))
                elif req.operation == OperationsEnum.join_room:
                    room = sorted(self.rooms_list, key=lambda x: x.token == req.token and x.available, reverse=True)[0]
                    client.room = room
                    room.players_list.append(client)
            print(req)


if __name__ == '__main__':
    server = Server()
    print(f'Server is running')
    server.listen_connections()
