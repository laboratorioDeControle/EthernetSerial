from PySide6.QtWidgets import QApplication
from gui.windows.ethernet_serial_driver_window import EthernetSerialWindow
import sys


app = QApplication(sys.argv)
window = EthernetSerialWindow()

app.exec()
