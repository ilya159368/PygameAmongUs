import socket
import sys
import time

from room import Room
from config import Config
import threading
import pickle
from protocol import *
from thread_ import CustomThread
from client import Client
from db_funcs import *


# from render import Vector2  # dont del


class Server(socket.socket):
    def __init__(self):
        super(Server, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((Config.server_ip, Config.server_port))
        self.listen(Config.server_listen)
        self.settimeout(10)
        self.listen_thread = CustomThread(self.listen_connections)
        self.to_exit = False

        self.clients_list = []
        self.rooms_list = []
        self.room_token = 111
        self.threads = []

        self.db = sqlite3.connect('database.sqlite', check_same_thread=False)
        self.cur = self.db.cursor()

    def listen_connections(self):
        while 1:
            try:
                conn, addr = self.accept()
            except socket.timeout as e:
                err = e.args[0]
                if err == 'timed out':
                    if self.to_exit:
                        self.close()
                        print('stopped')
                        sys.exit()
                    else:
                        continue
                else:
                    sys.exit(1)
            self.clients_list.append(Client(conn))
            print(f'Connected {conn}')
            new_thread = CustomThread(target=self.recv_data, args=(conn,))
            self.threads.append(new_thread)
            new_thread.start()

    def recv_data(self, conn: socket.socket):
        client = sorted(self.clients_list, key=lambda x: x.conn is conn, reverse=True)[0]
        while 1:
            try:
                data = b''
                while True:
                    rec = conn.recv(1024)
                    data += rec
                    if len(rec) < 1024:
                        break
                print(len(data), client.name)
            except socket.error:
                conn.close()
                if client.room:
                    client.room.delete_client(client)
                self.clients_list.remove(client)
                threading.currentThread().kill()
                return
            if not data:
                conn.close()
                if client.room:
                    client.room.delete_client(client)
                client.send_thread.kill()
                self.clients_list.remove(client)
                threading.currentThread().kill()
                return

            req = pickle.loads(data)

            if req.operation == 'delete':  # delete room if host disconnected
                room: Room = client.room
                client.send2all(Token('quit'))
                for c in room.players_list:
                    c.room = None
                self.rooms_list.remove(room)
            elif req.operation == 'quit':  # player quit room
                client.room.delete_client(client)
                client.send2all(Token('connected', cnt=len(client.room.players_list)))
                client.room = None

            # process game
            if req.in_game:
                if req.operation == 'move':
                    client.send2all(req)
                elif req.operation == 'voting':
                    req.kwargs['task_complete'] = client.room.tasks_progress
                    client.send2all(req, include_self=True)
                    client.room.start_voting()
                elif req.operation == 'kill':
                    client.send2all(req, include_self=True)
                    client.room.check_win()
                elif req.operation == 'task':
                    client.room.tasks_progress += 1
                    client.room.check_win()
                elif req.operation == 'vote':
                    choice_ = req.kwargs['choice_']
                    if choice_ is not None:
                        client.room.players_votes[choice_] += 1
                    else:
                        client.room.skip_votes += 1
                    client.send2all(Token('make_voted', id_=client.id), include_self=True)

            else:
                # process menu
                if req.operation == OperationsEnum.mouse_click:
                    print(req.pos_x, req.pos_y)
                elif req.operation == 'create':
                    for room in self.rooms_list:
                        if room.name == req.kwargs['name']:
                            conn.send(pickle.dumps(Token('create', status='bad')))
                            return
                    client.id = 0
                    token = self.room_token
                    room = Room(token, req.kwargs['name'], req.kwargs['max'])
                    self.room_token += 1
                    self.rooms_list.append(room)
                    client.room = room
                    client.color = room.colors_list[client.id]
                    room.players_list.append(client)
                    conn.send(pickle.dumps(Token('create', id=0, status='ok', token=room.token)))
                elif req.operation == 'find':
                    rooms = []
                    for room in sorted(self.rooms_list, key=lambda x: len(x.players_list),
                                       reverse=True)[:5]:
                        if room.available:
                            rooms.append(
                                (room.name, len(room.players_list), room.max_players, room.token))
                    out = Token('find', rooms=rooms)
                    conn.send(pickle.dumps(out))
                elif req.operation == 'join':
                    room = None
                    for r in self.rooms_list:
                        if r.token == req.kwargs['token'] and r.available:
                            room = r
                            break
                    if not room:
                        conn.send(pickle.dumps(Token('join', status='bad')))
                        return
                    client.room = room
                    client.id = room.new_player_id
                    room.new_player_id += 1
                    room.players_list.append(client)
                    client.color = room.colors_list[client.id]
                    client.send2all(
                        Token('connected', cnt=len(room.players_list), max_=room.max_players))
                    out = Token('join', id=client.id, status='ok', token=room.token,
                                cnt=len(room.players_list),
                                max_=room.max_players)  # TODO .+^ check if client quit
                    conn.send(pickle.dumps(out))
                    if len(room.players_list) == room.max_players:
                        room.available = False
                        client.room.init()
                        client.send2all(Token('init', players=[
                            (c.name, c.color, c.imposter) for c in client.room.players_list]),
                                        include_self=True)
                # ----------- тут начинается бд ---------------------------------------
                elif req.operation == 'sign_in':
                    result = sign_in(self.db, req.kwargs['name'], req.kwargs['password'], self.cur)
                    client.name = req.kwargs['name']
                    conn.send(
                        pickle.dumps(Token('sign_in', status=result, my_name=req.kwargs['name'])))

                elif req.operation == 'register':
                    result = register(self.db, req.kwargs['name'], req.kwargs['password'],
                                      req.kwargs['email'],
                                      self.cur)

                    conn.send(pickle.dumps(Token('register', status=result)))

                elif req.operation == 'change_name':
                    result = change_name(self.db, req.kwargs['old_name'], req.kwargs['new_name'],
                                         self.cur)
                    conn.send(pickle.dumps(Token('change_name', status=result)))
            if req.operation != 'move':
                print(req.operation)
            # print(self.rooms_list)
            # print(self.clients_list)

    def run(self):
        self.listen_thread.start()

    def exit(self):
        self.to_exit = True
        c: Client
        for c in self.clients_list:
            c.conn.close()
            c.send_thread.kill()
        for t in self.threads:
            t.kill()
        print('wait 10 secs...')
        sys.exit()


if __name__ == '__main__':
    server = Server()
    server.run()
    print(f'Server is running')
    # t = time.time()
    # print(t)
    try:
        while 1:
            # if time.time() == t + 10:
            #     server.exit()
            # print(time.time())
            if input() == 'q':
                server.exit()
    except KeyboardInterrupt:
        server.exit()
    except EOFError:
        server.exit()
