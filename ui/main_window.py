from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QSplitter, QStatusBar, QTextBrowser

from constants.constants import HOW_TO_SAVE_TONE
from core import Core
from ui.central_widget import CentralWidget
from ui.delete_tone_window import DeleteToneWindow
from ui.deque_log import DequeLog
from ui.file_dialogs import FileDialogHelper
from ui.gui_helper import GuiHelper
from ui.loading_animation import LoadingAnimation
from ui.rename_tone_window import RenameToneWindow
from ui.request_parameter_window import RequestParameterWindow
from ui.settings_window import SettingsWindow
from ui.top_widget import TopWidget
from ui.upload_tone_window import UploadToneWindow
from ui.user_tone_manager_window import UserToneManagerWindow
from utils.file_operations import FileOperations
from utils.utils import resource_path


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tone Mutant 1.1.5")
        self.setWindowIcon(QIcon(resource_path("resources/note.png")))

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.core = Core(self, self.status_bar)

        self.menu_bar = None
        self.reload_menu_bar()

        self.help_texbox = QTextBrowser(self)
        self.log_texbox = DequeLog(self)

        self.central_widget = CentralWidget(self)
        self.top_widget = TopWidget(self)

        self._setup_layout()

        self.loading_animation = LoadingAnimation(self)

        self.settings_window = None
        self.upload_tone_window = None
        self.rename_tone_window = None
        self.delete_tone_window = None
        self.user_tone_manager_window = None
        self.request_parameter_window = None

        # Initialize tone synchronization
        self.core.synchronize_tone_with_synth()

    def reload_menu_bar(self):
        self.menu_bar = GuiHelper.init_menu_bar(
            self,
            exit_callback=self.menu_exit_action,
            open_json_callback=self.show_open_json_dialog,
            save_json_callback=self.show_save_json_dialog,
            settings_callback=self.show_settings,
            how_to_save_callback=self.show_how_to_save_tone,
            request_parameter_callback=self.show_request_parameter_dialog,
            save_ton_callback=self.show_save_ton_dialog,
            upload_tone_callback=self.show_upload_tone_dialog,
            rename_tone_callback=self.show_rename_tone_dialog,
            delete_tone_callback=self.show_delete_tone_dialog,
            user_tone_manager_callback=self.show_user_tone_manager_window
        )
        self.setMenuBar(self.menu_bar)

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
            self.core.status_msg_signal.emit("File successfully saved!", 3000)

    def show_request_parameter_dialog(self):
        self.request_parameter_window = RequestParameterWindow(self)

    def show_save_ton_dialog(self):
        file_name = FileDialogHelper.save_ton_dialog(self)
        if file_name:
            try:
                self.core.start_ton_file_save_worker(file_name)
                self.top_widget.tone_name_label.setText(self.core.tone.name)
            except Exception as e:
                self.core.show_error_msg(str(e))

    def show_upload_tone_dialog(self):
        self.upload_tone_window = UploadToneWindow(self)

    def show_rename_tone_dialog(self):
        self.rename_tone_window = RenameToneWindow(self)

    def show_delete_tone_dialog(self):
        self.delete_tone_window = DeleteToneWindow(self)

    def show_user_tone_manager_window(self):
        self.user_tone_manager_window = UserToneManagerWindow(self)
        self.user_tone_manager_window.load_memory_tone_names()

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        self.loading_animation.center_loading_animation()

    @staticmethod
    def menu_exit_action():
        QCoreApplication.instance().quit()

    def exit_call(self):
        self.core.close_midi_ports()
        self.close()
