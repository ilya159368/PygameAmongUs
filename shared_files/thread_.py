import threading
import sys


class CustomThread(threading.Thread):
    def __init__(self, target, args=()):
        super(CustomThread, self).__init__(target=target, args=args)
        self.__flag = threading.Event()
        # self.__running = threading.Event()
        self.__flag.set()
        # self.__running.set()

    def suspend(self):
        self.__flag.clear()
        self.__flag.wait()

    def resume(self):
        self.__flag.set()

    def kill(self):
        # self.__running.clear()
        raise SystemExit

    def is_paused(self):
        return not self.__flag.isSet()

    def wait(self):
        self.__flag.wait()
