import os
from functools import partial

from PySide2.QtCore import Qt, QCoreApplication, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QSplitter, QStatusBar, QTextBrowser, QWidget, QMenu, QAction, QMenuBar, \
    QToolBar, QCheckBox

from constants.constants import HOW_TO_SAVE_TONE, CALIBRATION_TONES
from core import Core
from models.instrument import Instrument
from ui.central_widget import CentralWidget
from ui.delete_tone_window import DeleteToneWindow
from ui.deque_log import DequeLog
from ui.file_dialogs import FileDialogHelper
from ui.gui_helper import GuiHelper
from ui.loading_animation import LoadingAnimation
from ui.rename_tone_window import RenameToneWindow
from ui.request_parameter_window import RequestParameterWindow
from ui.settings_window import SettingsWindow
from ui.top_widget_mixer import TopWidgetMixer
from ui.upload_tone_window import UploadToneWindow
from ui.user_tone_manager_window import UserToneManagerWindow
from utils.file_operations import FileOperations
from utils.utils import resource_path


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tone Mutant 1.2.4")
        self.setWindowIcon(QIcon(resource_path("resources/note.png")))

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.core = Core(self, self.status_bar)

        self.menu_bar = None
        self.reload_menu_bar()

        self.help_texbox = QTextBrowser(self)
        self.log_texbox = DequeLog(self)

        self.central_widget = CentralWidget(self)
        self.top_widget = TopWidgetMixer(self)

        self.change_parent_tone_checkbox = QCheckBox("Random Parent Tone")
        self.change_parent_tone_checkbox.setStatusTip("When selected, the parent tone is randomly chosen before tone generation")
        self.change_parent_tone_checkbox.setStyleSheet("margin-left: 5px; margin-right: 5px;")
        self.change_parent_tone_checkbox.setChecked(True)

        self._init_toolbar()
        self._setup_layout()

        self.loading_animation = LoadingAnimation(self)

        self.settings_window = None
        self.upload_tone_window = None
        self.rename_tone_window = None
        self.delete_tone_window = None
        self.user_tone_manager_window = None
        self.request_parameter_window = None

        # Dimming overlay
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(255, 255, 255, 180);")  # Light gray
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.overlay.setVisible(False)  # Hidden by default

        # Initialize tone synchronization
        self.core.synchronize_tone_with_synth()

    def reload_menu_bar(self):
        self.menu_bar = QMenuBar(self)

        open_json_action = QAction(QIcon(resource_path('resources/open.png')), "Open Tone (JSON)", self)
        open_json_action.setStatusTip("Read tone information from a JSON-formatted file")
        open_json_action.triggered.connect(self.show_open_json_dialog)

        save_json_action = QAction(QIcon(resource_path('resources/save_purple.png')), "Save Tone (JSON)", self)
        save_json_action.setStatusTip("Save tone information as a JSON-formatted file")
        save_json_action.triggered.connect(self.show_save_json_dialog)

        save_action = QAction(QIcon(resource_path('resources/save.png')), "Save Tone (TON)", self)
        save_action.setStatusTip("Save tone as a TON file")
        save_action.triggered.connect(self.show_save_ton_dialog)

        midi_settings_action = QAction(QIcon(resource_path('resources/settings.png')), "Settings", self)
        midi_settings_action.setStatusTip("Open settings")
        midi_settings_action.triggered.connect(self.show_settings)

        exit_action = QAction(QIcon(resource_path('resources/exit.png')), "Exit", self)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.menu_exit_action)

        upload_tone_action = QAction(QIcon(resource_path('resources/piano_plus.png')),
                                     "Save Tone to Synthesizer's Memory",
                                     self)
        upload_tone_action.setStatusTip("Save current tone to the synthesizer's user memory section (801–900)")
        upload_tone_action.triggered.connect(self.show_upload_tone_dialog)

        rename_tone_action = QAction(QIcon(resource_path('resources/piano_pencil.png')), "Rename Tone", self)
        rename_tone_action.setStatusTip("Rename user tone (801–900)")
        rename_tone_action.triggered.connect(self.show_rename_tone_dialog)

        delete_tone_action = QAction(QIcon(resource_path('resources/piano_minus.png')), "Delete Tone", self)
        delete_tone_action.setStatusTip("Delete user tone (801–900)")
        delete_tone_action.triggered.connect(self.show_delete_tone_dialog)

        request_parameter_action = QAction(QIcon(resource_path('resources/request.png')), "Request Parameter",
                                           self)
        request_parameter_action.setStatusTip("Request a parameter from synthesizer")
        request_parameter_action.triggered.connect(self.show_request_parameter_dialog)

        user_tone_manager_action = QAction(QIcon(resource_path('resources/memory_manager.png')), "User Tone Manager",
                                           self)
        user_tone_manager_action.setStatusTip(
            "User Tone Manager allows you to save, rename, delete, and move tones within the synthesizer's user tone memory.")
        user_tone_manager_action.triggered.connect(self.show_user_tone_manager_window)

        # Calibration Tones sub-menu
        calibration_tone_menu = self.create_calibration_tone_menu()

        how_to_save_action = QAction(QIcon(resource_path('resources/help.png')), "Saving a TON File Using Synthesizer",
                                     self)
        how_to_save_action.setStatusTip("Instructions on how to use the synthesizer to save and export the tone")
        how_to_save_action.triggered.connect(self.show_how_to_save_tone)

        file_menu = QMenu("&File", self)
        file_menu.addAction(open_json_action)
        file_menu.addAction(save_json_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(midi_settings_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        self.menu_bar.addMenu(file_menu)

        tools_menu = QMenu("&Synthesizer Tools", self)
        tools_menu.addAction(user_tone_manager_action)
        tools_menu.addSeparator()
        tools_menu.addAction(upload_tone_action)
        tools_menu.addAction(rename_tone_action)
        tools_menu.addAction(delete_tone_action)

        if GuiHelper.is_expert_mode_enabled():
            tools_menu.addSeparator()
            tools_menu.addAction(request_parameter_action)

        tools_menu.addSeparator()
        tools_menu.addMenu(calibration_tone_menu)

        if not GuiHelper.has_user_memory():
            upload_tone_action.setEnabled(False)
            rename_tone_action.setEnabled(False)
            delete_tone_action.setEnabled(False)
            user_tone_manager_action.setEnabled(False)

        self.menu_bar.addMenu(tools_menu)

        help_menu = QMenu("&Help", self)
        help_menu.addAction(how_to_save_action)
        self.menu_bar.addMenu(help_menu)

        self.setMenuBar(self.menu_bar)

    def create_calibration_tone_menu(self):
        calibration_tone_menu = QMenu("Select Calibration Tone", self)
        calibration_tone_menu.setIcon(QIcon(resource_path("resources/note.png")))

        for instrument in CALIBRATION_TONES:
            action = QAction(QIcon(resource_path("resources/note.png")), instrument.name, self)
            action.setStatusTip(instrument.description)

            action.triggered.connect(partial(self.select_calibration_tone, instrument))
            calibration_tone_menu.addAction(action)

        return calibration_tone_menu

    def _init_toolbar(self):
        toolbar = QToolBar("Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setObjectName("toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)  # show both icon and text

        refresh_action = QAction(QIcon(resource_path("resources/refresh.png")), "Refresh", self)
        refresh_action.setStatusTip("Synchronize params from the synthesizer to the computer")
        refresh_action.triggered.connect(self.core.synchronize_tone_with_synth)

        random_tone_action = QAction(QIcon(resource_path("resources/random_wand.png")), "Generate Tone", self)
        random_tone_action.setStatusTip(
            "Generate Random Tone: set random main parameters and select 1–2 random DSP modules")
        random_tone_action.triggered.connect(self.core.on_randomize_tone_button_pressed)

        random_name_action = QAction(QIcon(resource_path("resources/random_wand.png")), "Random Name", self)
        random_name_action.setStatusTip("Generate random tone name")
        random_name_action.triggered.connect(self.core.generate_random_name)

        toolbar.addAction(refresh_action)
        toolbar.addSeparator()
        toolbar.addAction(random_tone_action)
        toolbar.addWidget(self.change_parent_tone_checkbox)
        toolbar.addSeparator()
        toolbar.addAction(random_name_action)

        self.addToolBar(toolbar)

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
            self.overlay.setVisible(True)
            self.core.load_tone_from_json(FileOperations.load_json(file_name))
            self.overlay.setVisible(False)

    def show_save_json_dialog(self):
        file_name = FileDialogHelper.save_json_dialog(self)
        if file_name:
            # if not self.core.tone.name:
            file_name_without_extension = os.path.splitext(os.path.basename(file_name))[0]
            self.core.tone.name = file_name_without_extension[:8]  # trim to first 8 symbols

            FileOperations.save_json(file_name, self.central_widget.get_json())
            self.top_widget.tone_name_input.setText(self.core.get_tone_id_and_name())
            self.core.status_msg_signal.emit("File successfully saved!", 3000)

    def show_request_parameter_dialog(self):
        self.request_parameter_window = RequestParameterWindow(self)

    def show_save_ton_dialog(self):
        file_name = FileDialogHelper.save_ton_dialog(self)
        if file_name:
            try:
                self.core.start_ton_file_save_worker(file_name)
                self.top_widget.tone_name_input.setText(self.core.get_tone_id_and_name())
            except Exception as e:
                self.core.show_error_msg(str(e))

    def show_upload_tone_dialog(self):
        self.upload_tone_window = UploadToneWindow(self)

    def show_rename_tone_dialog(self):
        self.rename_tone_window = RenameToneWindow(self)

    def show_delete_tone_dialog(self):
        self.delete_tone_window = DeleteToneWindow(self)

    def show_user_tone_manager_window(self):
        self.overlay.setVisible(True)
        self.user_tone_manager_window = UserToneManagerWindow(self)
        self.user_tone_manager_window.load_memory_tone_names()
        self.user_tone_manager_window.exec_()

        self.overlay.setVisible(False)
        self.core.synchronize_tone_signal.emit()  # when user tone manager is closed, synchronize tone with synth

    def select_calibration_tone(self, instrument: Instrument):
        self.core.select_calibration_tone(instrument)

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        self.loading_animation.center_loading_animation()
        self.overlay.setGeometry(0, 0, self.width(), self.height())

    @staticmethod
    def menu_exit_action():
        QCoreApplication.instance().quit()

    def exit_call(self):
        self.core.close_midi_ports()
        self.close()
