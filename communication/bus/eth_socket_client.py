import errno
import socket
import threading
from communication.signals import *


class EthSocketClient:
    @property
    def signals(self) -> CommunicationSignals:
        return self._signals

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def __init__(self):
        self._stop_dac: bool = False
        self._is_connected: bool = False

        self._signals: CommunicationSignals = CommunicationSignals()
        self._thread_dac: threading.Thread

        self._ip: str = ''
        self._port: int = 8081
        self._buff_size: int = 1024

        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__init_behaviour__()

    def __init_behaviour__(self):
        pass

    def __dac__(self):
        while not self._stop_dac:
            try:
                data: bytes = self._client_socket.recv(self._buff_size)
                self.signals.message_arrived.emit(data)

            except BlockingIOError as e:
                if e.errno == errno.EAGAIN:
                    pass

    def __start_dac__(self):
        self._stop_dac = False
        self._thread_dac = threading.Thread(target=self.__dac__, daemon=True)
        self._thread_dac.start()

    def __stop_dac__(self):
        self._stop_dac = True
        self._thread_dac.join()

    def connect(self, ip: str = '127.0.0.1', port: int = 8081, buff_size: int = 1024) -> (bool, str):
        self._ip = ip
        self._port = port
        self._buff_size = buff_size

        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._client_socket.setblocking(False)
            self._client_socket.connect_ex((self._ip, self._port))
            self.__start_dac__()
            self._is_connected = True

            return True, "Conectado com Sucesso ao Servidor: %s:%s" % (ip, port)

        except ConnectionRefusedError:
            return False, "Conexão com o Servidor: %s:%s Recusada!" % (ip, port)

    def disconnect(self):
        self.__stop_dac__()
        self._client_socket.close()

        self._is_connected = False

    def write(self, msg: bytes):
        self._client_socket.sendall(msg)
