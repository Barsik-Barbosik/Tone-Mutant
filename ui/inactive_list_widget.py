from PySide2.QtWidgets import QListWidget


class InactiveListWidget(QListWidget):
    def event(self, event):
        event.ignore()
        return super().event(event)

    def mousePressEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        event.ignore()

    def dragEnterEvent(self, event):
        event.ignore()

    def dragMoveEvent(self, event):
        event.ignore()

    def dragLeaveEvent(self, event):
        event.ignore()

    def dropEvent(self, event):
        event.ignore()
