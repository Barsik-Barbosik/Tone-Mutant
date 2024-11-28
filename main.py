import json
import os
import sys
import tempfile

from PySide2.QtCore import Qt, QCoreApplication, Signal, Slot
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow, QTextBrowser, \
    QStatusBar, QFileDialog, QSplitter

from constants.constants import HOW_TO_SAVE_TONE
from core import Core
from utils.utils import resource_path
from widgets.central_widget import CentralWidget
from widgets.deque_log import DequeLog
from widgets.gui_helper import GuiHelper
from widgets.settings_window import SettingsWindow
from widgets.top_widget import TopWidget


# Nuitka compiler options:
# nuitka-project: --output-filename=ToneMutant
# nuitka-project: --product-name=ToneMutant
# nuitka-project: --product-version=1.0.0
# nuitka-project: --file-version=1.0.0
# nuitka-project: --file-description="Tone editor for Casio keyboards"
# nuitka-project: --company-name="Barsik-Barbosik"
# nuitka-project: --standalone
# nuitka-project: --onefile
# nuitka-project: --onefile-windows-splash-screen-image={MAIN_DIRECTORY}/resources/splash.png
# nuitka-project: --enable-plugin=pyside2
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/resources=resources
# nuitka-project: --windows-icon-from-ico=resources/note.ico
# nuitka-project: --windows-console-mode=disable
# nuitka-project: --remove-output

class MainWindow(QMainWindow):
    status_msg_signal = Signal(str, int)

    def __init__(self, parent=None):
        # Splash screen (Nuitka)
        if "NUITKA_ONEFILE_PARENT" in os.environ:
            splash_filename = os.path.join(
                tempfile.gettempdir(),
                "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
            )

            if os.path.exists(splash_filename):
                os.unlink(splash_filename)

        super().__init__(parent)
        self.setWindowTitle("ToneMutant 1.0.0")
        self.setWindowIcon(QIcon(resource_path("resources/note.png")))

        self.core: Core = Core(self)

        self.menu_bar = GuiHelper.init_menu_bar(self)
        self.setMenuBar(self.menu_bar)

        self.help_texbox = QTextBrowser(self)
        self.log_texbox = DequeLog(self)

        self.central_widget = CentralWidget(self)
        self.central_widget.layout().setContentsMargins(10, 10, 0, 10)  # remove right margin

        self.top_widget = TopWidget(self)
        self.top_dock = GuiHelper.init_top_dock(self)
        self.addDockWidget(Qt.TopDockWidgetArea, self.top_dock)

        self.right_dock = GuiHelper.init_right_dock(self)

        splitter = QSplitter(self)
        splitter.addWidget(self.central_widget)
        splitter.addWidget(self.right_dock)
        splitter.setStretchFactor(0, 1)  # central_widget
        splitter.setStretchFactor(1, 3)  # right_dock
        self.setCentralWidget(splitter)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.settings_window = None

        self.status_msg_signal.connect(self.show_status_msg)

        self.core.synchronize_tone_with_synth()

    def show_help_text(self, text: str):
        self.help_texbox.setHtml(text)

    @Slot(str, int)
    def show_status_msg(self, text: str, msecs: int):
        self.status_bar.setStyleSheet("background-color: white; color: black")
        self.status_bar.showMessage(text, msecs)

    def show_error_msg(self, text: str):
        self.log_texbox.log("[ERROR] " + text)
        self.status_bar.setStyleSheet("background-color: white; color: red")
        self.status_bar.showMessage(text, 5000)

    def show_settings(self):
        self.settings_window = SettingsWindow(self)

    def show_how_to_save_tone(self):
        self.show_help_text(HOW_TO_SAVE_TONE)

    def show_open_json_dialog(self):
        options = QFileDialog.Options()
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_name, _ = file_dialog.getOpenFileName(self, "Open File", "", "JSON Files (*.json);;All Files (*)",
                                                   options=options)

        if file_name:
            with open(file_name, 'r') as file:
                self.core.load_tone_from_json(json.load(file))

    def show_save_json_dialog(self):
        options = QFileDialog.Options()
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_name, _ = file_dialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'w') as file:
                self.core.tone.name = os.path.splitext(os.path.basename(file_name))[0]
                file.write(self.central_widget.get_json())
                self.top_widget.tone_name_label.setText(self.core.tone.name)

    @staticmethod
    def menu_exit_action():
        QCoreApplication.instance().quit()

    def exit_call(self):
        self.core.close_midi_ports()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    with open(resource_path("resources/style.qss"), "r") as style_file:
        style = style_file.read()
        app.setStyleSheet(style)

    window = MainWindow()
    window.resize(1000, 600)
    window.show()
    app.aboutToQuit.connect(window.exit_call)
    sys.exit(app.exec_())
