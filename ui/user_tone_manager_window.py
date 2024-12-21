from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout

from constants.constants import INTERNAL_MEMORY_USER_TONE_COUNT
from ui.drag_and_drop_table import DragAndDropTable
from ui.loading_animation import LoadingAnimation
from utils.utils import resource_path
from utils.worker import Worker


class UserToneManagerWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle("User Tone Manager")
        self.setWindowIcon(QIcon(resource_path("resources/memory_manager.png")))

        self.core = parent.core
        self.items = []
        self.loading_animation = LoadingAnimation(self)

        self.resize(600, 500)
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the UI elements of the window."""
        main_layout = QVBoxLayout(self)

        label = QLabel()
        label.setText("<h2>User Tone Manager</h2>")
        label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(label)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)

        self.table_widget = DragAndDropTable(self)
        content_layout.addWidget(self.table_widget)

        # self.table_widget.connect(self.table_widget, QtCore.SIGNAL("itemDropped"), self.core.on_item_dropped)
        self.table_widget.itemSelectionChanged.connect(self.on_item_selection_changed)
        # self.table_widget.itemClicked.connect(self.on_item_selected)

        self.refresh_button = QPushButton(" Refresh")
        self.refresh_button.setIcon(QIcon(resource_path("resources/refresh.png")))
        self.refresh_button.setObjectName("manager-button")
        self.refresh_button.clicked.connect(self.load_memory_tone_names)

        self.upload_button = QPushButton(" Save Tone")
        self.upload_button.setIcon(QIcon(resource_path("resources/piano_plus.png")))
        self.upload_button.setObjectName("manager-button")
        self.upload_button.setEnabled(False)

        self.rename_button = QPushButton(" Rename")
        self.rename_button.setIcon(QIcon(resource_path("resources/piano_pencil.png")))
        self.rename_button.setObjectName("manager-button")
        self.rename_button.setEnabled(False)

        self.delete_button = QPushButton(" Delete")
        self.delete_button.setIcon(QIcon(resource_path("resources/piano_minus.png")))
        self.delete_button.setObjectName("manager-button")
        self.delete_button.setEnabled(False)

        self.apply_button = QPushButton(" Apply")
        self.apply_button.setIcon(QIcon(resource_path("resources/apply.png")))
        self.apply_button.setObjectName("manager-button")
        self.apply_button.setEnabled(False)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.rename_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addStretch()

        content_layout.addLayout(button_layout)

        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)
        self.show()

    def load_memory_tone_names(self):
        self.refresh_button.setEnabled(False)
        self.upload_button.setEnabled(False)
        self.rename_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        self.loading_animation.start()
        self.items = [None] * INTERNAL_MEMORY_USER_TONE_COUNT
        worker = Worker(self.core.request_user_memory_tone_names)
        worker.signals.error.connect(lambda error: self.core.show_error_msg(str(error[1])))
        worker.start()

    def add_item(self, tone_number, tone_name):
        if tone_number < INTERNAL_MEMORY_USER_TONE_COUNT:
            self.items[tone_number] = tone_name
            if len(self.items) == INTERNAL_MEMORY_USER_TONE_COUNT and all(self.items):
                self.refresh_list()
        else:
            raise ValueError("Tone number exceeds the limit")

    def refresh_list(self):
        """Refreshes the list in the GUI."""
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

        for item in self.items:
            self.table_widget.addItem(item)

        self.refresh_button.setEnabled(True)
        self.loading_animation.stop()

    def resizeEvent(self, event):
        super(UserToneManagerWindow, self).resizeEvent(event)
        self.loading_animation.center_loading_animation()

    def on_item_selection_changed(self):
        if self.table_widget.selectedItems():
            self.upload_button.setEnabled(True)
            self.rename_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.upload_button.setEnabled(False)
            self.rename_button.setEnabled(False)
            self.delete_button.setEnabled(False)
