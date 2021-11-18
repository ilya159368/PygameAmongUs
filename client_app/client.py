import socket
import datetime
import threading
import pickle
from config import Config
from protocol import *


class Client(socket.socket):

    queue_to = None
    queue_from = None

    def __init__(self):
        super(Client, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((Config.server_ip, Config.server_port))

        self.last_time_connected = datetime.datetime.now()
        self.recv_thread = threading.Thread(target=self.recv_data)
        self.recv_thread.start()
        # self.recv_thread.setDaemon(True)
        # self.send_thread.setDaemon(True)

    def reconnect(self, port):
        self.close()
        super(Client, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((Config.server_ip, port))

    def send_data(self):
        while 1:
            if not self.queue_to:
                threading.currentThread().suspend()
            data = self.queue_to.popleft()
            try:
                self.send(data)
                print('send')
            except socket.error:
                self.close()
                return -1

    def recv_data(self):
        while 1:
            try:
                data = self.recv(1024)
            except socket.error:
                self.close()
                return -1
            if not data:
                break
            self.queue_from.append(data)
            req = pickle.loads(data)
            if req.operation in (OperationsEnum.create_room, OperationsEnum.join_room):
                self.reconnect(req.port)
                print('reconnected')
