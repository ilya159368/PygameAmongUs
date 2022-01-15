import pickle
import threading
from collections import deque
from thread_ import CustomThread


class Client:
    def __init__(self, conn):
        self.conn = conn
        self.queue = deque()
        self.queue_from = deque()
        self.room = None
        self.send_thread = CustomThread(target=self.send_data)
        self.send_thread.start()
        # game attrs
        self.imposter = False
        self.name = 'undefined'
        self.alive = True

    def send_data(self):
        while 1:
            if self.queue:
                self.conn.send(pickle.dumps(self.queue.popleft()))
            if not self.queue:
                threading.currentThread().suspend()
                break

    def send2all(self, resp, include_self=False):
        for client_el in self.room.players_list:
            print(f'{self.name}->{client_el.name}')
            if include_self:
                client_el.queue.append(resp)
                client_el.send_thread.resume()
            else:
                if client_el is not self:
                    client_el.queue.append(resp)
                    client_el.send_thread.resume()

    def to_queue(self, resp):
        self.queue.append(resp)
        if self.send_thread.is_paused():
            self.send_thread.resume()