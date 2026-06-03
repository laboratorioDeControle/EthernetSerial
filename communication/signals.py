from PySide6.QtCore import QObject, Signal


class CommunicationSignals(QObject):
    update_bus = Signal()
    message_arrived = Signal(bytes)
    message_to_send = Signal(dict)
