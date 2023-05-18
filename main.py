import sys

from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtWidgets import QApplication, QStatusBar, QMainWindow, QMenu, QAction, QMenuBar, QTextBrowser, \
    QDockWidget, \
    QWidget, QHBoxLayout, QTabWidget

from central_widget import CentralWidget
from midi_settings_window import MidiSettingsWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CT-X Controller")

        self.menu_bar = self.init_menu_bar()
        self.setMenuBar(self.menu_bar)

        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.layout().setContentsMargins(10, 10, 0, 10)  # remove right margin

        self.help_texbox = QTextBrowser()
        self.right_dock = self.init_right_dock(self.help_texbox)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        self.status_bar = self.init_status_bar()
        self.setStatusBar(self.status_bar)

        self.midi_settings_window = None

        self.central_widget.redraw_help_msg()

    def init_menu_bar(self):
        menu_bar = QMenuBar(self)

        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        open_action = QAction("&Open Tone (TON)", self)
        open_action.setStatusTip("Open TON-file")
        open_action.setEnabled(False)
        save_action = QAction("&Save Tone (TON)", self)
        save_action.setStatusTip("Save tone as TON-file")
        save_action.setEnabled(False)
        open_json_action = QAction("Open Tone (JSON)", self)
        open_json_action.setStatusTip("Read tone information from JSON-formatted file")
        save_json_action = QAction("Save Tone (JSON)", self)
        save_json_action.setStatusTip("Save tone information as JSON-formatted file")
        save_txt_action = QAction("Save Tone Description as text (TXT)", self)
        save_txt_action.setStatusTip("Save tone description as TXT-file")
        midi_settings_action = QAction("&MIDI settings", self)
        midi_settings_action.setStatusTip("Open MIDI settings")
        midi_settings_action.triggered.connect(self.show_midi_settings)
        exit_action = QAction("&Exit", self)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.menu_exit_action)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(open_json_action)
        file_menu.addAction(save_json_action)
        file_menu.addAction(save_txt_action)
        file_menu.addSeparator()
        file_menu.addAction(midi_settings_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        return menu_bar

    def init_right_dock(self, help_texbox):
        right_dock = QDockWidget("Right Dock", self)
        right_dock.setTitleBarWidget(QWidget())
        right_dock.setFloating(False)

        inter_widget = QWidget(self)
        inter_layout = QHBoxLayout(self)
        inter_layout.addWidget(help_texbox)
        inter_widget.setLayout(inter_layout)

        tab_widget = QTabWidget(self)
        tab_widget.setMinimumHeight(400)
        tab_widget.setMinimumWidth(300)
        tab_widget.addTab(inter_widget, "Info / Help")

        outer_widget = QWidget(self)
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 10, 10, 10)  # remove left margin
        outer_layout.addWidget(tab_widget)
        outer_widget.setLayout(outer_layout)

        right_dock.setWidget(outer_widget)

        return right_dock

    def show_help_msg(self, text: str):
        self.help_texbox.setHtml(text)

    def init_status_bar(self):
        status_bar = QStatusBar(self)
        status_bar.showMessage("Hello!!", 1000)

        return status_bar

    def show_status_msg(self, text: str, msecs: int):
        self.status_bar.setStyleSheet("background-color: white; color: black")
        self.status_bar.showMessage(text, msecs)

    def show_error_msg(self, text: str):
        self.status_bar.setStyleSheet("background-color: white; color: red")
        self.status_bar.showMessage(text, 5000)

    def show_midi_settings(self):
        self.midi_settings_window = MidiSettingsWindow()

    @staticmethod
    def menu_exit_action():
        QCoreApplication.instance().quit()

    def exit_call(self):
        self.central_widget.midi_service.close_midi_ports()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    with open("style.qss", "r") as style_file:
        style = style_file.read()
        app.setStyleSheet(style)

    window = MainWindow()
    window.resize(1000, 600)
    window.show()
    app.aboutToQuit.connect(window.exit_call)
    sys.exit(app.exec_())
