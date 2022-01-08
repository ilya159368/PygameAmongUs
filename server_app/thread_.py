import threading
import sys


class CustomThread(threading.Thread):
    def __init__(self, target, args=()):
        super(CustomThread, self).__init__(target=target, args=args)
        self.target, self.args = target, args
        self.__flag = threading.Event()
        self.__running = threading.Event()
        self.__flag.set()
        self.__running.set()

    def run(self) -> None:
        while self.__running.is_set():
            self.__flag.wait()
            self.target(*self.args)

    def suspend(self):
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def kill(self):
        self.resume()
        self.__running.clear()

    def is_paused(self):
        return not self.__flag.is_set()

    # def wait(self):
    #     self.__flag.wait()
