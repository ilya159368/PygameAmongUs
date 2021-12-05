import pickle
import threading
from collections import deque
from shared_files.thread_ import CustomThread


class Client:

    def __init__(self, conn):
        self.conn = conn
        self.queue = deque()
        self.room = None
        self.send_thread = CustomThread(target=self.send_data)
        self.send_thread.start()

    def send_data(self):
        while 1:
            if not self.queue:
                threading.currentThread().suspend()
            self.conn.send(pickle.dumps(self.queue.popleft()))
