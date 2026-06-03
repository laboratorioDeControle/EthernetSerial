import serial
import serial.tools.list_ports
from usbx import usb
import threading
import time

from communication.signals import *


def get_serial_ports() -> list:
    result = []

    for port in serial.tools.list_ports.comports(include_links=False):
        result.append(port.name)

    return result


class Serial:
    @property
    def signals(self) -> CommunicationSignals:
        return self._signals

    @property
    def is_connected(self) -> bool:
        return self._serial.is_open

    def __init__(self, incoming_bytes: int = 150, read_timeout: float = 0.01):
        self._stop_dac: bool = False

        self._signals: CommunicationSignals = CommunicationSignals()

        self._thread_bus_update: threading.Thread
        self._thread_dac: threading.Thread

        self._serial: serial.Serial = serial.Serial()
        self._incoming_bytes: int = incoming_bytes
        self._read_timeout: float = read_timeout

        self.__init_behaviour__()

    def __init_behaviour__(self):
        self._thread_bus_update = threading.Thread(target=self.__bus_update__, daemon=True)
        self._thread_bus_update.start()

    def __bus_update__(self):
        last_devices: list = usb.get_devices()

        while not self._stop_dac:
            devices: list = usb.get_devices()

            if last_devices != devices:
                self.signals.update_bus.emit()

            last_devices = devices.copy()
            time.sleep(1.0)

    def __dac__(self):
        while not self._stop_dac:
            try:
                raw: bytes = self._serial.read(self._incoming_bytes)
                if raw != b'':
                    self.signals.message_arrived.emit(raw)
                    self._serial.flush()

            except Exception as error:
                pass

    def __start_dac__(self):
        self._stop_dac = False
        self._thread_dac = threading.Thread(target=self.__dac__, daemon=True)
        self._thread_dac.start()

    def __stop_dac__(self):
        self._stop_dac = True
        self._thread_dac.join()

    def connect(self, com_port: str = "", baudrate: int = 9600, incoming_bytes: int = 150,
                read_timeout: float = 0.01) -> bool:

        self._incoming_bytes = incoming_bytes
        self._read_timeout = read_timeout

        try:
            self._serial = serial.Serial(com_port, baudrate, timeout=self._read_timeout)
            self.__start_dac__()
            return True
        except serial.serialutil.SerialException:
            self._serial = serial.Serial()
            return False

    def disconnect(self) -> bool:
        if self._serial.is_open:
            self._serial.close()

        self.__stop_dac__()
        self._serial = serial.Serial()
        return True

    def write(self, msg: bytes):
        if self._serial.is_open:
            self._serial.write(msg)
