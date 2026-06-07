from datetime import datetime
from PySide6.QtWidgets import QWidget, QGridLayout, QTextEdit, QPushButton, QComboBox, QCheckBox, QFileDialog


class BusMsgLogWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._layout: QGridLayout = QGridLayout()

        self._bt_clear: QPushButton = QPushButton("Limpar")
        self._bt_save: QPushButton = QPushButton("Salvar")

        self._chb_register_msg: QCheckBox = QCheckBox("Registrar Mensagens")
        self._cb_parsing: QComboBox = QComboBox()

        self._te_msgs: QTextEdit = QTextEdit()

        self._msgs: list = []

        self.__init_ui__()
        self.__init_backend__()

    def __init_ui__(self):
        parsing: list = ["BIN", "HEX", "DEC", "ASCII"]

        self.setLayout(self._layout)
        self._layout.addWidget(self._te_msgs, 0, 0, 1, 4)
        self._layout.addWidget(self._chb_register_msg, 1, 0, 1, 1)
        self._layout.addWidget(self._cb_parsing, 1, 1, 1, 1)
        self._layout.addWidget(self._bt_clear, 1, 2, 1, 1)
        self._layout.addWidget(self._bt_save, 1, 3, 1, 1)

        for parse in parsing:
            self._cb_parsing.addItem(parse)


    def __init_backend__(self):
        self._bt_clear.clicked.connect(self.clear)
        self._bt_save.clicked.connect(self.save)

        self._cb_parsing.currentTextChanged.connect(self.__update_parsing_mode__)

    @staticmethod
    def __hex_field__(data) -> str:
        hex_field: str = hex(data)
        hex_field_split: list = hex_field.split("x")

        if len(hex_field_split[1]) == 1:
            hex_field_split[1] = "0" + hex_field_split[1]

        hex_field = hex_field_split[0] + "x" + hex_field_split[1]
        return hex_field

    def __update_text__(self, parse_mode: str):
        te_log_scroll = self._te_msgs.verticalScrollBar()
        old_scroll_ratio = te_log_scroll.value() / (te_log_scroll.maximum() or 1)

        text: str = ""

        for msg in self._msgs:
            bus: str = msg["bus"]
            direction: str = msg["direction"]
            timestamp: str = msg["timestamp"] + ": "
            data: bytes = msg["data"]

            data_text: str = "["

            for index, field in enumerate(data):
                field_text: str = ""
                if parse_mode == "DEC":
                    data_text += str(int(field))

                elif parse_mode == "HEX":
                    data_text += self.__hex_field__(field)

                elif parse_mode == "BIN":
                    data_text += f"{int(field):08b}"

                elif parse_mode == "ASCII":
                    data_text += chr(int(field))

                if index != len(data) - 1:
                    data_text += field_text + ", "
                else:
                    data_text += field_text + "]"

            line: str = timestamp + "[" + direction + "]" + "[" + bus + "] -> " + data_text + "\n"
            text += line

        self._te_msgs.setText(text)
        te_log_scroll.setValue(round(old_scroll_ratio * te_log_scroll.maximum()))

    def __update_parsing_mode__(self):
        current_parse: str = self._cb_parsing.currentText()
        self.__update_text__(current_parse)


    def append(self, bus_name: str, direction: str, timestamp: str ,data: bytes):
        if self._chb_register_msg.isChecked():
            self._msgs.append({
                "bus": bus_name,
                "direction": direction,
                "timestamp": timestamp,
                "data": data
            })

            self.__update_text__(self._cb_parsing.currentText())

    def clear(self):
        self._msgs = []
        self._te_msgs.setText("")

    def save(self):
        file_name: tuple = QFileDialog.getSaveFileName(self, "Tráfego de Mensagens",
                                                       filter="Arquivo de Texto (*.txt)")

        if file_name[0] != "":
            f = open(file_name[0], "w")
            f.write(self._te_msgs.toPlainText())
            f.close()

    def serialize(self) -> dict:
        return {
            "register_msgs": int(self._chb_register_msg.isChecked()),
            "parse": self._cb_parsing.currentIndex()
        }

    def deserialize(self, parameters: dict):
        self._chb_register_msg.setChecked(bool(parameters["register_msgs"]))
        self._cb_parsing.setCurrentIndex(parameters["parse"])