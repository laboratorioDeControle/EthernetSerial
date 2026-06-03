from datetime import datetime
from PySide6.QtWidgets import (QWidget, QGridLayout, QLineEdit, QComboBox, QPushButton, QGroupBox, QLabel, QTextEdit,
                               QCheckBox, QFileDialog)

from communication.bus.serial import Serial, get_serial_ports
from communication.bus.eth_socket_server import EthSocketServer


class EthernetSerialDriverWidget(QWidget):
    @property
    def eth_ip(self) -> str:
        if self._le_eth_ip.text() != "":
            return self._le_eth_ip.text()

        self._le_eth_ip.setText("127.0.0.1")
        return "127.0.0.1"

    @eth_ip.setter
    def eth_ip(self, value: str):
        self._le_eth_ip.setText(value)

    @property
    def eth_port(self) -> int:
        port: int = 8081

        try:
            port = int(self._le_eth_port.text())

        except ValueError:
            self._le_eth_port.setText(str(port))

        finally:
            if port <= 0 or port > 65535:
                port = 8081
                self._le_eth_port.setText(str(port))
            return port

    @eth_port.setter
    def eth_port(self, value: int):
        self._le_eth_port.setText(str(value))

    @property
    def eth_buffer_size(self) -> int:
        buff_size: int = 1024

        try:
            buff_size = int(self._le_eth_incoming_bytes.text())

        except ValueError:
            self._le_eth_incoming_bytes.setText(str(buff_size))

        finally:
            return buff_size

    @eth_buffer_size.setter
    def eth_buffer_size(self, value: int):
        self._le_eth_incoming_bytes.setText(str(value))

    @property
    def serial_com_port(self) -> str:
        return self._cb_serial_com_ports.currentText()

    @serial_com_port.setter
    def serial_com_port(self, value: str):
        index: int = -1

        for i in range(self._cb_serial_com_ports.count()):
            if self._cb_serial_com_ports.itemText(i) == value:
                index = i

        if index != -1:
            self._cb_serial_com_ports.setCurrentIndex(index)

    @property
    def serial_baud_rate(self) -> int:
        baud_rate: int = 115200

        try:
            baud_rate = int(self._le_serial_baud_rate.text())

        except ValueError:
            self._le_serial_baud_rate.setText(str(baud_rate))

        finally:
            return baud_rate

    @serial_baud_rate.setter
    def serial_baud_rate(self, value: int):
        self._le_serial_baud_rate.setText(str(value))

    @property
    def serial_buffer_size(self) -> int:
        buff_size: int = 150

        try:
            buff_size = int(self._le_serial_incoming_bytes.text())

        except ValueError:
            self._le_serial_incoming_bytes.setText(str(buff_size))

        finally:
            return buff_size

    @serial_buffer_size.setter
    def serial_buffer_size(self, value: int):
        self._le_serial_incoming_bytes.setText(str(value))

    @property
    def serial_read_timeout(self) -> float:
        read_timeout: float = 0.01

        try:
            read_timeout = float(self._le_serial_read_timeout.text())

        except ValueError:
            self._le_serial_read_timeout.setText(str(read_timeout))

        finally:
            return read_timeout

    @serial_read_timeout.setter
    def serial_read_timeout(self, value: float):
        self._le_serial_read_timeout.setText(str(value))

    @property
    def register_msgs(self) -> bool:
        return self._chb_register_msgs.isChecked()

    @register_msgs.setter
    def register_msgs(self, value: bool):
        self._chb_register_msgs.setChecked(value)

    @property
    def auto_transmit(self) -> bool:
        return self._chb_auto_transmit.isChecked()

    @auto_transmit.setter
    def auto_transmit(self, value: bool):
        self._chb_auto_transmit.setChecked(value)

    @property
    def send_msg_use_hex(self) -> bool:
        return self._chb_use_hex.isChecked()

    @send_msg_use_hex.setter
    def send_msg_use_hex(self, value: bool):
        self._chb_use_hex.setChecked(value)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._layout: QGridLayout = QGridLayout()

        self._gb_ethernet: QGroupBox = QGroupBox("Ethernet:")
        self._bt_start_stop_server: QPushButton = QPushButton("Abrir Servidor")
        self._le_eth_ip: QLineEdit = QLineEdit("127.0.0.1")
        self._le_eth_port: QLineEdit = QLineEdit("8081")
        self._le_eth_incoming_bytes: QLineEdit = QLineEdit("1024")

        self._gb_serial: QGroupBox = QGroupBox("Serial:")
        self._bt_serial_open_close: QPushButton = QPushButton("Abrir Comunicação")
        self._le_serial_baud_rate: QLineEdit = QLineEdit("115200")
        self._le_serial_incoming_bytes: QLineEdit = QLineEdit("150")
        self._le_serial_read_timeout: QLineEdit = QLineEdit("0.01")
        self._cb_serial_com_ports: QComboBox = QComboBox()

        self._gb_send: QGroupBox = QGroupBox("Envio de Mensagem:")
        self._le_msg_to_send: QLineEdit = QLineEdit("[]")
        self._chb_use_hex: QCheckBox = QCheckBox("Hexadecimal")
        self._chb_auto_transmit: QCheckBox = QCheckBox("Comunicar Barramentos")
        self._bt_send_eth: QPushButton = QPushButton("Enviar via Ethernet")
        self._bt_send_serial: QPushButton = QPushButton("Enviar via Serial")

        self._gb_log: QGroupBox = QGroupBox("Tráfego de Mensagens:")
        self._te_log: QTextEdit = QTextEdit()
        self._bt_export_log: QPushButton = QPushButton("Salvar")
        self._bt_clear_log: QPushButton = QPushButton("Limpar")
        self._chb_register_msgs: QCheckBox = QCheckBox("Registrar Mensagens")

        self._serial_bus: Serial = Serial()
        self._eth_bus: EthSocketServer = EthSocketServer()

        self._send_last_use_hex: bool = False

        self.__init_ui__()
        self.__init_backend__()

    def __init_ui__(self):
        self.setLayout(self._layout)

        lyt_bus: QGridLayout = QGridLayout()
        gb_bus: QGroupBox = QGroupBox("Barramentos:")
        gb_bus.setLayout(lyt_bus)

        lyt_eth: QGridLayout = QGridLayout()
        self._gb_ethernet.setLayout(lyt_eth)
        lyt_eth.addWidget(QLabel("IP:"), 0, 0, 1, 1)
        lyt_eth.addWidget(self._le_eth_ip, 0, 1, 1, 1)
        lyt_eth.addWidget(QLabel("Porta:"), 1, 0, 1, 1)
        lyt_eth.addWidget(self._le_eth_port, 1, 1, 1, 1)
        lyt_eth.addWidget(QLabel("Tamanho da Mensagem (Bytes):"), 2, 0, 1, 1)
        lyt_eth.addWidget(self._le_eth_incoming_bytes, 2, 1, 1, 1)
        lyt_eth.addWidget(self._bt_start_stop_server, 3, 0, 1, 2)

        lyt_serial: QGridLayout = QGridLayout()
        self._gb_serial.setLayout(lyt_serial)
        lyt_serial.addWidget(QLabel("Porta:"), 0, 0, 1, 1)
        lyt_serial.addWidget(self._cb_serial_com_ports, 0, 1, 1, 1)
        lyt_serial.addWidget(QLabel("Baudrate:"), 1, 0, 1, 1)
        lyt_serial.addWidget(self._le_serial_baud_rate, 1, 1, 1, 1)
        lyt_serial.addWidget(QLabel("Tempo Máximo de Leitura (segundos):"), 2, 0, 1, 1)
        lyt_serial.addWidget(self._le_serial_read_timeout, 2, 1, 1, 1)
        lyt_serial.addWidget(QLabel("Tamanho da Mensagem (Bytes):"), 3, 0, 1, 1)
        lyt_serial.addWidget(self._le_serial_incoming_bytes, 3, 1, 1, 1)
        lyt_serial.addWidget(self._bt_serial_open_close, 4, 0, 1, 2)

        lyt_bus.addWidget(self._gb_ethernet, 0, 0, 1, 1)
        lyt_bus.addWidget(self._gb_serial, 0, 1, 1, 1)
        lyt_bus.addWidget(self._chb_auto_transmit, 1, 0, 1, 1)

        lyt_send: QGridLayout = QGridLayout()
        self._gb_send.setLayout(lyt_send)
        lyt_send.addWidget(QLabel("Mensagem:"), 0, 0, 1, 1)
        lyt_send.addWidget(self._le_msg_to_send, 0, 1, 1, 5)
        lyt_send.addWidget(self._chb_use_hex, 1, 3, 1, 1)
        lyt_send.addWidget(self._bt_send_eth, 1, 4, 1, 1)
        lyt_send.addWidget(self._bt_send_serial, 1, 5, 1, 1)

        lyt_log: QGridLayout = QGridLayout()
        self._gb_log.setLayout(lyt_log)
        lyt_log.addWidget(self._te_log, 0, 0, 1, 5)
        lyt_log.addWidget(self._bt_clear_log, 1, 3, 1, 1)
        lyt_log.addWidget(self._bt_export_log, 1, 4, 1, 1)
        lyt_log.addWidget(self._chb_register_msgs, 1, 2, 1, 1)

        self._layout.addWidget(gb_bus, 0, 0, 1, 1)
        self._layout.addWidget(self._gb_send, 1, 0, 1, 2)
        self._layout.addWidget(self._gb_log, 2, 0, 1, 2)

        self._te_log.setEnabled(True)
        self._chb_register_msgs.setChecked(True)

    def __init_backend__(self):
        self._bt_start_stop_server.clicked.connect(self.__bt_eth_start_stop_server_callback__)
        self._bt_serial_open_close.clicked.connect(self.__bt_serial_open_close_callback__)
        self._bt_clear_log.clicked.connect(self.__bt_clear_log_callback__)
        self._bt_export_log.clicked.connect(self.__bt_export_log_callback__)
        self._bt_send_eth.clicked.connect(self.__bt_send_eth_callback__)
        self._bt_send_serial.clicked.connect(self.__bt_send_serial_callback__)

        self._chb_use_hex.checkStateChanged.connect(self.__chb_use_hexadecimal_change_callback__)

        self._serial_bus.signals.update_bus.connect(self.__com_port_update_callback__)
        self._serial_bus.signals.message_arrived.connect(self.__serial_msg_arrive__)

        self._eth_bus.signals.message_arrived.connect(self.__eth_msg_arrive__)

        self.__com_port_update_callback__()

    def __bt_eth_start_stop_server_callback__(self):
        if not self._eth_bus.is_opened:
            self._bt_start_stop_server.setText("Fechar Servidor")
            self._eth_bus.start(self.eth_ip, self.eth_port, self.eth_buffer_size)

        else:
            self._bt_start_stop_server.setText("Abrir Servidor")
            self._eth_bus.stop()

    def __bt_serial_open_close_callback__(self):
        if not self._serial_bus.is_connected:
            if self.serial_com_port != "":
                self._bt_serial_open_close.setText("Fechar Comunicação")
                self._serial_bus.connect(self.serial_com_port, self.serial_baud_rate,
                                         self.serial_buffer_size, self.serial_read_timeout)

        else:
            self._bt_serial_open_close.setText("Abrir Comunicação")
            self._serial_bus.disconnect()

    def __format_msg__(self) -> bytes:
        msg_orig: str = self._le_msg_to_send.text()
        msg = msg_orig.replace("[", "").replace("]", "").replace(" ", "")

        msg_split: list = msg.split(",")

        result: list = []

        for index, field in enumerate(msg_split):
            if field != '':
                number: int = 0

                if self._chb_use_hex.isChecked():
                    number = int(field, 16)
                else:
                    number = int(field)

                result.append(number)

        return bytes(result)

    def __format_msg_dec_hex__(self) -> str:
        msg_orig: str = self._le_msg_to_send.text()
        msg = msg_orig.replace("[", "").replace("]", "").replace(" ", "")

        msg_split: list = msg.split(",")
        result: str = "["

        for index, field in enumerate(msg_split):
            if field != '':
                number: int = 0

                if self._send_last_use_hex:
                    number = int(field, 16)
                    result += str(number)
                else:
                    number = int(field)
                    number_hex: str = hex(number)
                    number_hex_split: list = number_hex.split("x")

                    if len(number_hex_split[1]) == 1:
                        number_hex_split[1] = "0" + number_hex_split[1]

                    number_hex = number_hex_split[0] + "x" + number_hex_split[1]

                    result += number_hex

                if index != len(msg_split) - 1:
                    result += ", "

        result += "]"
        return result

    def __chb_use_hexadecimal_change_callback__(self):
        use_hex: bool = self._chb_use_hex.isChecked()
        self._send_last_use_hex = not use_hex

        new_msg: str = self.__format_msg_dec_hex__()
        self._le_msg_to_send.setText(new_msg)

    def __bt_clear_log_callback__(self):
        self._te_log.setText("")

    def __bt_export_log_callback__(self):
        file_name: tuple = QFileDialog.getSaveFileName(self, "Tráfego de Mensagens",
                                                       filter="Arquivo de Texto (*.txt)")

        if file_name[0] != "":
            f = open(file_name[0], "w")
            f.write(self._te_log.toPlainText())
            f.close()

    def __bt_send_eth_callback__(self):
        if self._eth_bus.have_client:
            msg: bytes = self.__format_msg__()
            self._eth_bus.write(msg)

    def __bt_send_serial_callback__(self):
        if self._serial_bus.is_connected:
            msg: bytes = self.__format_msg__()
            self._serial_bus.write(msg)

    def __com_port_update_callback__(self):
        self._cb_serial_com_ports.clear()
        com_ports: list = get_serial_ports()

        for com in com_ports:
            self._cb_serial_com_ports.addItem(com)

    def __serial_msg_arrive__(self, msg: bytes):
        if self.register_msgs:
            self.log_append("SERIAL", msg)

        if self._eth_bus.have_client and self._chb_auto_transmit.isChecked():
            self._eth_bus.write(msg)

    def __eth_msg_arrive__(self, msg: bytes):
        if self.register_msgs:
            self.log_append("ETHERNET", msg)

        if self._serial_bus.is_connected and self._chb_auto_transmit.isChecked():
            self._serial_bus.write(msg)

    def log_append(self, com_bus: str, data: bytes):
        date_time: str = datetime.today().strftime('%H:%M:%S') + ": "
        msg: str = "["

        for index, field in enumerate(data):
            hex_field: str = hex(field)
            hex_field_split: list = hex_field.split("x")

            if len(hex_field_split[1]) == 1:
                hex_field_split[1] = "0" + hex_field_split[1]

            hex_field = hex_field_split[0] + "x" + hex_field_split[1]

            if index != len(data) - 1:
                msg += hex_field + ", "
            else:
                msg += hex_field + "]"

        msg = date_time + "[" + com_bus + "] -> " + msg + "\n"

        te_log_scroll = self._te_log.verticalScrollBar()
        old_scroll_ratio = te_log_scroll.value() / (te_log_scroll.maximum() or 1)
        self._te_log.setText(self._te_log.toPlainText() + msg)
        te_log_scroll.setValue(round(old_scroll_ratio * te_log_scroll.maximum()))

    def serialize(self) -> dict:
        return {
            "eth_ip": self.eth_ip,
            "eth_port": self.eth_port,
            "eth_buff_size": self.eth_buffer_size,
            "serial_com_port": self.serial_com_port,
            "serial_baud_rate": self.serial_baud_rate,
            "serial_buffer_size": self.serial_buffer_size,
            "serial_read_timeout": self.serial_read_timeout,
            "register_msgs": int(self.register_msgs),
            "auto_transmit": int(self.auto_transmit),
            "msg_to_send": self._le_msg_to_send.text(),
            "send_msg_use_hex": int(self.send_msg_use_hex)
        }

    def deserialize(self, parameters: dict) -> None:
        self.eth_ip = parameters["eth_ip"]
        self.eth_port = parameters["eth_port"]
        self.eth_buffer_size = parameters["eth_buff_size"]
        self.serial_com_port = parameters["serial_com_port"]
        self.serial_baud_rate = parameters["serial_baud_rate"]
        self.serial_buffer_size = parameters["serial_buffer_size"]
        self.serial_read_timeout = parameters["serial_read_timeout"]
        self.register_msgs = bool(parameters["register_msgs"])
        self.auto_transmit = bool(parameters["auto_transmit"])
        self._le_msg_to_send.setText(parameters["msg_to_send"])
        self.send_msg_use_hex = bool(parameters["send_msg_use_hex"])
