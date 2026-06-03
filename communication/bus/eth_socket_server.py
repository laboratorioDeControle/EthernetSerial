import socket
import threading
import select
from communication.signals import *


class EthSocketServer:
    @property
    def signals(self) -> CommunicationSignals:
        return self._signals

    @property
    def is_opened(self) -> bool:
        return self._is_opened

    @property
    def have_client(self) -> bool:
        return self._have_client

    def __init__(self):
        self._stop_dac: bool = False
        self._is_opened: bool = False

        self._signals: CommunicationSignals = CommunicationSignals()
        self._thread_dac: threading.Thread

        self._ip: str = ''
        self._port: int = 8081
        self._buff_size: int = 1024

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._have_client: bool = False
        self._conn = None

        self.__init_behaviour__()

    def __init_behaviour__(self):
        pass

    def __dac__(self):
        while not self._stop_dac:
            inputs: list = [self._server_socket]
            outputs: list = []

            readable, writable, exceptional = select.select(
                inputs, outputs, inputs, 1
            )

            for s in readable:
                if s is self._server_socket:
                    self._conn, addr = s.accept()
                    inputs.append(self._conn)
                    self._have_client = True
                    threading.Thread(target=self.__handle_client__, args=(self._conn, addr, self._buff_size)).start()

    def __start_dac__(self):
        self._stop_dac = False
        self._thread_dac = threading.Thread(target=self.__dac__, daemon=True)
        self._thread_dac.start()

    def __stop_dac__(self):
        self._stop_dac = True
        self._thread_dac.join()

    def __handle_client__(self, client_connection, address, buff_size):
        raw_data: bytes = client_connection.recv(buff_size)

        while raw_data != b'' and not self._stop_dac:
            self.signals.message_arrived.emit(raw_data)
            raw_data: bytes = client_connection.recv(buff_size)

        client_connection.close()
        self._have_client = False

    def start(self, ip: str = '', port: int = 8081, buff_size: int = 1024):
        self._ip = ip
        self._port = port
        self._buff_size = buff_size

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((self._ip, self._port))
        self._server_socket.listen()

        self.__start_dac__()

        self._is_opened = True

    def stop(self):
        self.__stop_dac__()
        self._server_socket.close()

        self._is_opened = False
        self._have_client = False

    def write(self, msg: bytes):
        if self._conn is not None:
            self._conn.send(msg)
