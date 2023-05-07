import sys

from PyQt5.QtWidgets import QApplication, QStatusBar, QMainWindow, QMenu, QAction, QMenuBar

from central_widget import CentralWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CT-X Controller")
        self.setStyleSheet("QWidget {font-size: 11pt;}")

        self.menu_bar = self.init_menu_bar()
        self.setMenuBar(self.menu_bar)

        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)

        self.status_bar = self.init_status_bar()
        self.setStatusBar(self.status_bar)

    def init_menu_bar(self):
        menu_bar = QMenuBar(self)

        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        open_action = QAction("&Open tone", self)
        open_action.setStatusTip('Open TON-file')
        save_action = QAction("&Save tone", self)
        save_action.setStatusTip('Save TON-file')
        midi_settings_action = QAction("&MIDI settings", self)
        midi_settings_action.setStatusTip('Open MIDI settings')
        exit_action = QAction("&Exit", self)
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.exit_call)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(midi_settings_action)
        file_menu.addAction(exit_action)

        return menu_bar

    def init_status_bar(self):
        status_bar = QStatusBar(self)
        status_bar.setStyleSheet("background-color: white;")
        # statusBar.setStyleSheet("color: red")
        status_bar.showMessage("Hello!!", 1000)

        return status_bar

    def exit_call(self):
        print('Exit app')
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
