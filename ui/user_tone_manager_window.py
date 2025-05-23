import os
import time

from PySide2 import QtCore
from PySide2.QtCore import Qt, QDir
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDialog, QApplication, QTableWidgetItem, \
    QFileDialog

from constants.constants import INTERNAL_MEMORY_USER_TONE_COUNT, USER_TONE_TABLE_ROW_OFFSET
from ui.drag_and_drop_table import DragAndDropTable
from ui.file_table import FileTable
from ui.loading_animation import LoadingAnimation
from utils.file_operations import FileOperations
from utils.utils import resource_path
from utils.worker import Worker


class UserToneManagerWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("User Tone Manager")
        self.setWindowIcon(QIcon(resource_path("resources/memory_manager.png")))
        self.setWindowFlags(QtCore.Qt.Window)

        self.core = parent.core
        self.path = ""  # Replace with the actual directory path
        self.items = []
        self.selectedItems = []
        self.loading_animation = LoadingAnimation(self)

        self.resize(960, 670)
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the UI elements of the window."""
        main_layout = QVBoxLayout(self)

        label = QLabel()
        label.setText("<h2>User Tone Manager</h2>")
        label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(label)

        self.change_folder_button = QPushButton(" PC Folder")
        self.change_folder_button.setIcon(QIcon(resource_path("resources/open.png")))
        self.change_folder_button.setObjectName("manager-left-button")
        self.change_folder_button.clicked.connect(self.select_folder)

        self.move_from_pc = QPushButton(" Upload")
        self.move_from_pc.setIcon(QIcon(resource_path("resources/right.png")))
        self.move_from_pc.setObjectName("manager-left-button")
        self.move_from_pc.clicked.connect(self.on_move_from_pc)

        left_button_layout = QVBoxLayout()
        left_invisible_title = QLabel("")
        left_button_layout.addWidget(left_invisible_title)
        left_button_layout.addWidget(self.change_folder_button)
        left_button_layout.addWidget(self.move_from_pc)
        left_button_layout.addStretch()

        file_table_layout = QVBoxLayout()

        file_table_title = QLabel("<b>PC User Data Files</b>")
        file_table_title.setAlignment(QtCore.Qt.AlignCenter)
        file_table_layout.addWidget(file_table_title)

        self.file_table_widget = FileTable(self, external_drag_drop_finished_callback=self.on_save_tone_file)
        self.populate_file_table()

        file_table_layout.addWidget(self.file_table_widget)

        table_layout = QVBoxLayout()

        user_memory_title = QLabel("<b>Synthesizer's Internal Memory</b>")
        user_memory_title.setAlignment(QtCore.Qt.AlignCenter)
        table_layout.addWidget(user_memory_title)

        self.table_widget = DragAndDropTable(self,
                                             table_row_offset=USER_TONE_TABLE_ROW_OFFSET,
                                             editing_finished_callback=self.on_editing_finished,
                                             internal_drag_drop_finished_callback=self.on_drag_and_drop,
                                             external_drag_drop_finished_callback=self.on_load_tone_file)
        table_layout.addWidget(self.table_widget)

        self.refresh_button = QPushButton(" Refresh")
        self.refresh_button.setIcon(QIcon(resource_path("resources/refresh.png")))
        self.refresh_button.setObjectName("manager-button")
        self.refresh_button.clicked.connect(self.load_memory_tone_names)

        self.upload_button = QPushButton(" Save Here")
        self.upload_button.setIcon(QIcon(resource_path("resources/piano_plus.png")))
        self.upload_button.setObjectName("manager-button")
        self.upload_button.clicked.connect(self.upload_tone)

        self.rename_button = QPushButton(" Rename")
        self.rename_button.setIcon(QIcon(resource_path("resources/pencil.png")))
        self.rename_button.setObjectName("manager-button")
        self.rename_button.clicked.connect(self.enable_text_editing)

        self.delete_button = QPushButton(" Delete")
        self.delete_button.setIcon(QIcon(resource_path("resources/eraser.png")))
        self.delete_button.setObjectName("manager-button")
        self.delete_button.clicked.connect(self.delete_tone)

        self.move_up_button = QPushButton(" Move Up")
        self.move_up_button.setIcon(QIcon(resource_path("resources/up.png")))
        self.move_up_button.setObjectName("manager-button")
        self.move_up_button.clicked.connect(self.on_move_up_button)

        self.move_down_button = QPushButton(" Move Down")
        self.move_down_button.setIcon(QIcon(resource_path("resources/down.png")))
        self.move_down_button.setObjectName("manager-button")
        self.move_down_button.clicked.connect(self.on_move_down_button)

        self.move_to_pc = QPushButton(" Download")
        self.move_to_pc.setIcon(QIcon(resource_path("resources/left.png")))
        self.move_to_pc.setObjectName("manager-button")
        self.move_to_pc.clicked.connect(self.on_move_to_pc)

        self.disable_controls()

        # "COPY" & "PASTE" buttons?

        button_layout = QVBoxLayout()
        right_invisible_title = QLabel("")
        button_layout.addWidget(right_invisible_title)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.rename_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.move_up_button)
        button_layout.addWidget(self.move_down_button)
        button_layout.addWidget(self.move_to_pc)
        button_layout.addStretch()

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.addLayout(left_button_layout)
        content_layout.addLayout(file_table_layout)
        content_layout.addLayout(table_layout)
        content_layout.addLayout(button_layout)

        main_layout.addLayout(content_layout)

        self.file_table_widget.itemSelectionChanged.connect(self.on_file_selection_changed)
        self.table_widget.itemSelectionChanged.connect(self.on_item_selection_changed)

    def disable_controls(self):
        self.table_widget.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.upload_button.setEnabled(False)
        self.rename_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.move_up_button.setEnabled(False)
        self.move_down_button.setEnabled(False)
        self.move_from_pc.setEnabled(False)
        self.move_to_pc.setEnabled(False)
        QApplication.processEvents()

    def enable_controls(self):
        self.table_widget.setEnabled(True)
        self.refresh_button.setEnabled(True)

        if self.table_widget.selectedItems():
            if len(self.table_widget.selectedItems()) == 1:
                self.upload_button.setEnabled(True)
                self.rename_button.setEnabled(True)
                if self.table_widget.currentRow() > 0:
                    self.move_up_button.setEnabled(True)
                else:
                    self.move_up_button.setEnabled(False)
                if self.table_widget.currentRow() < 99:
                    self.move_down_button.setEnabled(True)
                else:
                    self.move_down_button.setEnabled(False)
            else:
                self.upload_button.setEnabled(False)
                self.rename_button.setEnabled(False)
                self.move_up_button.setEnabled(False)
                self.move_down_button.setEnabled(False)
            self.delete_button.setEnabled(True)
            self.move_to_pc.setEnabled(True)
        else:
            self.upload_button.setEnabled(False)
            self.rename_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.move_up_button.setEnabled(False)
            self.move_down_button.setEnabled(False)
            self.move_to_pc.setEnabled(False)

        if self.file_table_widget.selectedItems():
            self.move_from_pc.setEnabled(True)
        else:
            self.move_from_pc.setEnabled(False)

    def load_memory_tone_names(self):
        self.loading_animation.start()

        # Refresh the file table
        self.populate_file_table()

        # Refresh the user memory table
        self.disable_controls()
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

        self.enable_controls()
        self.loading_animation.stop()

    def resizeEvent(self, event):
        super(UserToneManagerWindow, self).resizeEvent(event)
        self.loading_animation.center_loading_animation()

    def on_item_selection_changed(self):
        self.file_table_widget.itemSelectionChanged.disconnect(self.on_file_selection_changed)
        self.file_table_widget.clearSelection()
        self.file_table_widget.itemSelectionChanged.connect(self.on_file_selection_changed)
        self.enable_controls()

    def on_move_up_button(self):
        if self.table_widget.selectedItems() and len(self.table_widget.selectedItems()) == 1:
            row_number = self.table_widget.currentRow()
            if row_number > 0:  # Ensure it's not the first row
                self.loading_animation.start()
                self.disable_controls()

                # Swap names with the row above
                for col in range(self.table_widget.columnCount()):
                    current_item = self.table_widget.item(row_number, col)
                    above_item = self.table_widget.item(row_number - 1, col)

                    current_text = current_item.text() if current_item else ""
                    above_text = above_item.text() if above_item else ""

                    if current_item:
                        current_item.setText(above_text)
                    if above_item:
                        above_item.setText(current_text)

                # Update the selection
                self.table_widget.blockSignals(True)
                self.table_widget.selectRow(row_number - 1)
                self.table_widget.blockSignals(False)

                worker = Worker(self.move_row, row_number, row_number - 1)
                worker.signals.error.connect(lambda error: self.core.show_error_msg(str(error[1])))
                worker.signals.finished.connect(self.on_move_row_worker_finished)
                worker.start()

    def on_move_down_button(self):
        if self.table_widget.selectedItems() and len(self.table_widget.selectedItems()) == 1:
            row_number = self.table_widget.currentRow()
            if row_number < self.table_widget.rowCount() - 1:  # Ensure it's not the last row
                self.loading_animation.start()
                self.disable_controls()

                # Swap names with the row below
                for col in range(self.table_widget.columnCount()):
                    current_item = self.table_widget.item(row_number, col)
                    below_item = self.table_widget.item(row_number + 1, col)

                    current_text = current_item.text() if current_item else ""
                    below_text = below_item.text() if below_item else ""

                    if current_item:
                        current_item.setText(below_text)
                    if below_item:
                        below_item.setText(current_text)

                # Update the selection
                self.table_widget.blockSignals(True)
                self.table_widget.selectRow(row_number + 1)
                self.table_widget.blockSignals(False)

                worker = Worker(self.move_row, row_number, row_number + 1)
                worker.signals.error.connect(lambda error: self.core.show_error_msg(str(error[1])))
                worker.signals.finished.connect(self.on_move_row_worker_finished)
                worker.start()

    def on_drag_and_drop(self, original_row, new_row):
        self.loading_animation.start()
        self.disable_controls()
        worker = Worker(self.move_row, original_row, new_row)
        worker.signals.error.connect(lambda error: self.core.show_error_msg(str(error[1])))
        worker.signals.finished.connect(self.on_move_row_worker_finished)
        worker.start()

    def on_move_row_worker_finished(self):
        self.enable_controls()
        self.loading_animation.stop()

    def move_row(self, original_row, new_row):
        if original_row > new_row:
            # Moving selected item up (affected items are moving down)
            original_row_data = self.core.load_tone_data(original_row + USER_TONE_TABLE_ROW_OFFSET)
            for i in range(original_row - 1, new_row - 1, -1):
                row_data = self.core.load_tone_data(i + USER_TONE_TABLE_ROW_OFFSET)
                self.core.save_tone_data(i + USER_TONE_TABLE_ROW_OFFSET + 1, row_data)
            self.core.save_tone_data(new_row + USER_TONE_TABLE_ROW_OFFSET, original_row_data)
        elif original_row < new_row:
            # Moving selected item down (affected items are moving up)
            original_row_data = self.core.load_tone_data(original_row + USER_TONE_TABLE_ROW_OFFSET)
            for i in range(original_row + 1, new_row + 1):
                row_data = self.core.load_tone_data(i + USER_TONE_TABLE_ROW_OFFSET)
                self.core.save_tone_data(i + USER_TONE_TABLE_ROW_OFFSET - 1, row_data)
            self.core.save_tone_data(new_row + USER_TONE_TABLE_ROW_OFFSET, original_row_data)

        # self.loading_animation.stop()

    def upload_tone(self):
        if self.table_widget.selectedItems() and len(self.table_widget.selectedItems()) == 1:
            self.loading_animation.start()
            self.disable_controls()
            tone_number = self.table_widget.currentRow() + USER_TONE_TABLE_ROW_OFFSET
            worker = Worker(self.core.upload_current_tone, tone_number)
            worker.signals.error.connect(lambda error: self.core.show_error_msg(str(error[1])))
            worker.start()

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
            self.disable_controls()
            tone_number = self.table_widget.row(current_item) + USER_TONE_TABLE_ROW_OFFSET
            new_tone_name = current_item.text()
            worker = Worker(self.core.rename_tone, tone_number, new_tone_name)
            worker.signals.error.connect(lambda error: self.core.show_error_msg(str(error[1])))
            worker.start()

    def delete_tone(self):
        if self.table_widget.selectedItems():
            self.selectedItems = self.table_widget.selectedItems()
            self.disable_controls()
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

    def populate_file_table(self):
        """Populates the file table with .ton files from the given directory."""
        dir = QDir(self.path)
        filtered_files = dir.entryList(["*.ton"], QDir.Files)
        self.file_table_widget.setRowCount(len(filtered_files))
        for row, file_name in enumerate(filtered_files):
            item = QTableWidgetItem(file_name)
            self.file_table_widget.setItem(row, 0, item)

    def on_file_selection_changed(self):
        self.table_widget.itemSelectionChanged.disconnect(self.on_item_selection_changed)
        self.table_widget.clearSelection()
        self.enable_controls()
        self.table_widget.itemSelectionChanged.connect(self.on_item_selection_changed)

    def on_load_tone_file(self, file_name, row_number):
        self.loading_animation.start()
        self.disable_controls()

        tone_number = row_number + USER_TONE_TABLE_ROW_OFFSET
        full_path = os.path.join(self.path, file_name)
        self.core.tone_manager_upload_ton_file(tone_number, FileOperations.load_binary_file(full_path))

    def on_save_tone_file(self, rows_data):
        self.loading_animation.start()

        for row_data in rows_data:
            row_number, tone_name = row_data.split(":", 1)  # Split by the colon to separate row and text
            tone_number = int(row_number) + USER_TONE_TABLE_ROW_OFFSET
            file_name = tone_name + ".ton"

            if file_name:
                try:
                    full_path = os.path.join(self.path, file_name)
                    self.core.tone_manager_save_ton_file(full_path, tone_number)

                    if len(rows_data) > 1:
                        time.sleep(1)  # TODO: Replace with a better solution

                except Exception as e:
                    self.core.show_error_msg(str(e))

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.path = folder_path
            self.populate_file_table()

    def on_move_from_pc(self):
        file_name = self.file_table_widget.currentItem().text()
        row_number = 99  # Default to the last row

        empty_items = self.table_widget.findItems("No Data", Qt.MatchExactly)
        if empty_items:
            row_number = self.table_widget.row(empty_items[0])

        self.on_load_tone_file(file_name, row_number)

    def on_move_to_pc(self):
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            rows_data = []
            for item in selected_items:
                rows_data.append(f"{item.row()}:{item.text()}")  # Store row number and item text

            self.on_save_tone_file(rows_data)

    def closeEvent(self, event):
        """Ensures proper cleanup when the window is closed."""
        # Stop any running animations
        if self.loading_animation:
            self.loading_animation.stop()
            self.loading_animation.deleteLater()
            self.loading_animation = None

        # Disconnect signals
        try:
            self.file_table_widget.itemSelectionChanged.disconnect(self.on_file_selection_changed)
            self.table_widget.itemSelectionChanged.disconnect(self.on_item_selection_changed)
        except TypeError:
            pass  # Avoid errors if they were already disconnected

        # Delete dynamically created widgets
        for widget in [
            self.file_table_widget,
            self.table_widget,
            self.change_folder_button,
            self.move_from_pc,
            self.refresh_button,
            self.upload_button,
            self.rename_button,
            self.delete_button,
            self.move_up_button,
            self.move_down_button,
            self.move_to_pc
        ]:
            if widget:
                widget.deleteLater()

        # Clear lists
        self.items.clear()
        self.selectedItems.clear()

        # Call parent close event
        super().closeEvent(event)
