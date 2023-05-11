import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QStatusBar, QMainWindow, QMenu, QAction, QMenuBar, QTextBrowser, QDockWidget, \
    QWidget, QHBoxLayout

from central_widget import CentralWidget
from midi_settings_window import MidiSettingsWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CT-X Controller")
        self.setStyleSheet("QWidget {font-size: 11pt;}")

        self.menu_bar = self.init_menu_bar()
        self.setMenuBar(self.menu_bar)

        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)

        self.help_texbox = QTextBrowser()
        self.right_dock = self.init_right_dock(self.help_texbox)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        self.status_bar = self.init_status_bar()
        self.setStatusBar(self.status_bar)

        self.midi_settings_window = None

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
        midi_settings_action.triggered.connect(self.show_midi_settings)
        exit_action = QAction("&Exit", self)
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.exit_call)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(midi_settings_action)
        file_menu.addAction(exit_action)

        return menu_bar

    def init_right_dock(self, help_texbox):
        right_dock = QDockWidget('Help', self)
        right_dock.setTitleBarWidget(QWidget())
        right_dock.setFloating(False)

        help_widget = QWidget(self)
        hbox_layout = QHBoxLayout(self)
        hbox_layout.addWidget(help_texbox)
        help_widget.setLayout(hbox_layout)
        right_dock.setWidget(help_widget)

        return right_dock

    def show_help_msg(self, text: str):
        self.help_texbox.setHtml(text)

    def init_status_bar(self):
        status_bar = QStatusBar(self)
        status_bar.setStyleSheet("background-color: white;")
        status_bar.showMessage("Hello!!", 1000)

        return status_bar

    def show_status_msg(self, text: str, msecs: int):
        self.status_bar.setStyleSheet("background-color: white; color: black")
        self.status_bar.showMessage(text, msecs)

    def show_error_msg(self, text: str):
        self.status_bar.setStyleSheet("background-color: white; color: red")
        self.status_bar.showMessage(text)

    def show_midi_settings(self):
        self.midi_settings_window = MidiSettingsWindow()

    def exit_call(self):
        self.central_widget.midi.Close()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.aboutToQuit.connect(window.exit_call)
    sys.exit(app.exec())
