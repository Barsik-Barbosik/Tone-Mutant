from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDialog

from constants.constants import INTERNAL_MEMORY_USER_TONE_COUNT, USER_TONE_TABLE_ROW_OFFSET
from ui.drag_and_drop_table import DragAndDropTable
from ui.loading_animation import LoadingAnimation
from utils.utils import resource_path
from utils.worker import Worker


class UserToneManagerWindow(QDialog):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle("User Tone Manager")
        self.setWindowIcon(QIcon(resource_path("resources/memory_manager.png")))
        self.setWindowFlags(QtCore.Qt.Window)

        self.core = parent.core
        self.items = []
        self.selectedItems = []
        self.loading_animation = LoadingAnimation(self)

        self.resize(600, 500)
        self._setup_ui()
        # self.show()

    def _setup_ui(self):
        """Sets up the UI elements of the window."""
        main_layout = QVBoxLayout(self)

        label = QLabel()
        label.setText("<h2>User Tone Manager</h2>")
        label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(label)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)

        self.table_widget = DragAndDropTable(self,
                                             table_row_offset=USER_TONE_TABLE_ROW_OFFSET,
                                             editing_finished_callback=self.on_editing_finished,
                                             drag_drop_finished_callback=self.on_drag_drop_finished)
        content_layout.addWidget(self.table_widget)

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
        self.rename_button.clicked.connect(self.enable_text_editing)
        self.rename_button.setEnabled(False)

        self.delete_button = QPushButton(" Delete")
        self.delete_button.setIcon(QIcon(resource_path("resources/piano_minus.png")))
        self.delete_button.setObjectName("manager-button")
        self.delete_button.clicked.connect(self.delete_tone)
        self.delete_button.setEnabled(False)

        # "COPY" & "PASTE" buttons?
        # "MOVE UP" & "MOVE DOWN" buttons?

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.rename_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        content_layout.addLayout(button_layout)

        main_layout.addLayout(content_layout)

        self.table_widget.itemSelectionChanged.connect(self.on_item_selection_changed)

        self.setLayout(main_layout)

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
            if len(self.table_widget.selectedItems()) == 1:
                self.upload_button.setEnabled(True)
                self.rename_button.setEnabled(True)
            else:
                self.upload_button.setEnabled(False)
                self.rename_button.setEnabled(False)
            self.delete_button.setEnabled(True)
        else:
            self.upload_button.setEnabled(False)
            self.rename_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def on_drag_drop_finished(self, original_row, new_row):
        if original_row > new_row:
            # Moving up
            print(f"Save row {original_row} to temp")
            for i in range(original_row - 1, new_row - 1, -1):
                print(f"Move row {i} to {i + 1}")
            print(f"Paste temp to row {new_row}")
        elif original_row < new_row:
            # Moving down
            print(f"Save row {original_row} to temp")
            for i in range(original_row + 1, new_row + 1):
                print(f"Move row {i} to {i - 1}")
            print(f"Paste temp to row {new_row}")
        else:
            # No movement
            print("No movement")

    def enable_text_editing(self):
        selected_row = self.table_widget.currentRow()
        if selected_row != -1:
            item = self.table_widget.item(selected_row, 0)
            if item:
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table_widget.editItem(item)

    def on_editing_finished(self):
        """Callback method to handle the end of editing."""
        current_item = self.table_widget.currentItem()
        if current_item:
            self.loading_animation.start()
            tone_number = self.table_widget.row(current_item) + USER_TONE_TABLE_ROW_OFFSET
            new_tone_name = current_item.text()
            worker = Worker(self.core.rename_tone, tone_number, new_tone_name)
            worker.signals.error.connect(lambda error: self.core.show_error_msg(str(error[1])))
            worker.start()

    def delete_tone(self):
        if self.table_widget.selectedItems():
            self.selectedItems = self.table_widget.selectedItems()
            self.delete_next_tone()

    def delete_next_tone(self):
        if self.selectedItems:
            self.loading_animation.start()
            selected_item = self.selectedItems.pop()
            tone_number = self.table_widget.row(selected_item) + USER_TONE_TABLE_ROW_OFFSET
            tone_name = selected_item.text()
            worker = Worker(self.core.delete_next_tone, tone_number, tone_name)
            worker.signals.error.connect(lambda error: self.core.show_error_msg(str(error[1])))
            worker.start()
        else:
            self.core.after_all_selected_tones_deleted()
