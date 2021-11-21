import socket
import datetime
import threading
import pickle
import sys
from config import Config
# from shared_files.protocol import *
from shared_files.thread_ import CustomThread


class Client(socket.socket):
    def __init__(self, app):
        super(Client, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.settimeout(1)
        self.connect_server()
        if self.connected:
            self.queue_from = app.queue_from
            self.queue_to = app.queue_to
            self.last_time_connected = datetime.datetime.now()
            self.recv_thread = CustomThread(target=self.recv_data)
            self.send_thread = CustomThread(target=self.send_data)
            app.send_thread = self.send_thread
            self.send_thread.start()
            self.recv_thread.start()
            app.add_before_exit(self.close)
            app.add_before_exit(self.send_thread.kill)
            app.add_before_exit(self.recv_thread.kill)
        else:
            app.offline = True
        app.connecting = False

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
            except socket.timeout as e:
                err = e.args[0]
                if err == 'timed out':
                    continue
                else:
                    sys.exit(1)
            except socket.error:
                self.close()
                return -1
            else:
                if not data:
                    print('server error')
                    sys.exit(0)
                else:
                    self.queue_from.append(data)
            # req = pickle.loads(data)

    def connect_server(self):
        try:
            self.connect((Config.server_ip, Config.server_port))
            self.connected = True
        except socket.error:
            self.connected = False

