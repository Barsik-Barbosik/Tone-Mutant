from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QSplitter, QStatusBar, QTextBrowser

from constants.constants import HOW_TO_SAVE_TONE
from core import Core
from ui.central_widget import CentralWidget
from ui.deque_log import DequeLog
from ui.file_dialogs import FileDialogHelper
from ui.gui_helper import GuiHelper
from ui.request_parameter_window import RequestParameterWindow
from ui.settings_window import SettingsWindow
from ui.top_widget import TopWidget
from utils.file_operations import FileOperations
from utils.utils import resource_path


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ToneMutant 1.0.1")
        self.setWindowIcon(QIcon(resource_path("resources/note.png")))

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Initialize Core
        self.core = Core(self, self.status_bar)

        # Initialize UI components
        self.menu_bar = GuiHelper.init_menu_bar(
            self,
            exit_callback=self.menu_exit_action,
            open_json_callback=self.show_open_json_dialog,
            save_json_callback=self.show_save_json_dialog,
            settings_callback=self.show_settings,
            how_to_save_callback=self.show_how_to_save_tone,
            request_parameter_callback=self.show_request_parameter_dialog,
            download_tone_callback=self.show_download_tone_dialog
        )
        self.setMenuBar(self.menu_bar)

        self.help_texbox = QTextBrowser(self)
        self.log_texbox = DequeLog(self)

        self.central_widget = CentralWidget(self)
        self.top_widget = TopWidget(self)

        self._setup_layout()

        self.settings_window = None
        self.request_parameter_window = None

        # Initialize tone synchronization
        self.core.synchronize_tone_with_synth()

    def _setup_layout(self):
        self.central_widget.layout().setContentsMargins(10, 10, 0, 10)

        self.top_dock = GuiHelper.init_top_dock(self)
        self.addDockWidget(Qt.TopDockWidgetArea, self.top_dock)

        self.right_dock = GuiHelper.init_right_dock(self)

        splitter = QSplitter(self)
        splitter.addWidget(self.central_widget)
        splitter.addWidget(self.right_dock)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        self.setCentralWidget(splitter)

    def show_settings(self):
        self.settings_window = SettingsWindow(self)

    def show_help_text(self, text: str):
        self.help_texbox.setHtml(text)

    def show_how_to_save_tone(self):
        self.help_texbox.setHtml(HOW_TO_SAVE_TONE)

    def show_open_json_dialog(self):
        file_name = FileDialogHelper.open_json_dialog(self)
        if file_name:
            self.core.load_tone_from_json(FileOperations.load_json(file_name))

    def show_save_json_dialog(self):
        file_name = FileDialogHelper.save_json_dialog(self)
        if file_name:
            FileOperations.save_json(file_name, self.central_widget.get_json())
            self.top_widget.tone_name_label.setText(self.core.tone.name)

    def show_request_parameter_dialog(self):
        self.request_parameter_window = RequestParameterWindow(self)

    def show_download_tone_dialog(self):
        # if val_result < 801 or val_result > 900:
        #     raise Exception("Cannot download from Tone number {0}".format(val_result))

        # TEST: Get a User Tone from slot 900 and save into slot 899
        download_from = 900
        upload_to = 899

        try:
            current_tone = self.core.tyrant_midi_service.tone_read(0, memory=3)
            print(current_tone)

            # downloaded_tone = self.core.tyrant_midi_service.bulk_download(download_from - 801, memory=1, category=3)
            # In order to save the downloaded tone as a TON-file, the first 20 bytes and the last 4 bytes need to be added
            # self.core.tyrant_midi_service.bulk_upload(upload_to - 801, downloaded_tone, memory=1, category=3)
            # print(downloaded_tone)

            # Restore default MIDI-in callback
            self.core.close_midi_ports()
            self.core.open_midi_ports()
        except Exception:
            pass

    @staticmethod
    def menu_exit_action():
        QCoreApplication.instance().quit()

    def exit_call(self):
        self.core.close_midi_ports()
        self.close()
