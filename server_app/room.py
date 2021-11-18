import socket
import pickle
import threading

from config import Config
from thread_ import CustomThread
from player import Player


class Room(socket.socket):
    players_list = []
    available = True

    def __init__(self, port, name, max_players):
        super(Room, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.bind((Config.server_ip, port))
        self.listen(Config.room_listen)
        self.name, self.max_players = name, max_players

        self.listen_thread = threading.Thread(target=self.listen_connections)
        self.listen_thread.start()

    def listen_connections(self):
        while 1:
            conn, addr = self.accept()
            self.players_list.append(Player(conn))
            new_thread = CustomThread(target=self.recv_data, args=(conn, addr))
            new_thread.start()

    def recv_data(self, conn: socket.socket, addr):
        while 1:
            data = conn.recv(1024)
            curr_player = sorted(self.players_list, key=lambda x: x.conn is conn)[0]
            if not data:
                conn.close()
                threading.currentThread().kill()
                self.players_list.remove(curr_player)
                break
            req = pickle.loads(data)
            for player in self.players_list:
                if player is not curr_player:
                    player.queue.append(req)
                    player.send_thread.resume()
