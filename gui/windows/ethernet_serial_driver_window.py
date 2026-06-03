from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QWidget
from gui.widgets.ethernet_serial_driver_widget import EthernetSerialDriverWidget
from backend.tools import *


class EthernetSerialWindow(QMainWindow):
    @property
    def __version__(self) -> str:
        return str(self._major_version) + "." + str(self._minor_version) + "." + str(self._revision)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._major_version: int = 0
        self._minor_version: int = 0
        self._revision: int = 1

        self._main_widget: EthernetSerialDriverWidget = EthernetSerialDriverWidget()

        self.__init_ui__()

    def __init_ui__(self):
        self.setWindowTitle("Ethernet <-> Serial Driver - v" + self.__version__)
        self.setWindowIcon(QIcon("images/icone.ico"))

        self.setCentralWidget(self._main_widget)
        self.setFixedSize(800, 600)

        self.deserialize()

        self.show()

    def closeEvent(self, event):
        self.serialize()
        event.accept()

    def serialize(self):
        parameters: dict = self._main_widget.serialize()
        dict_to_json("configs.json", parameters)

    def deserialize(self):
        parameters: dict = json_to_dict("configs.json")
        if parameters != {}:
            self._main_widget.deserialize(parameters)
