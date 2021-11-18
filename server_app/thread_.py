import threading


class CustomThread(threading.Thread):
    def __init__(self, target, args=()):
        super(CustomThread, self).__init__(target=target, args=args)
        self.__flag = threading.Event()
        self.__running = threading.Event()
        self.__flag.set()
        self.__running.set()

    # def run(self) -> None:
    #     while self.__running.isSet():
    #

    def suspend(self):
        self.__flag.clear()
        self.__flag.wait()

    def resume(self):
        self.__flag.set()

    def kill(self):
        self.__running.clear()

    def is_paused(self):
        return not self.__flag.isSet()

    def wait(self):
        self.__flag.wait()
