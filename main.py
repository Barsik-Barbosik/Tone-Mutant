import sys

from PyQt5.QtWidgets import QApplication, QStatusBar, QMainWindow

from CentralWidget import CentralWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CT-X Controller")
        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)

        self.status_bar = QStatusBar(self)
        self.status_bar.setStyleSheet("background-color: white;")
        # self.statusBar.setStyleSheet("color: red")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hello!!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
