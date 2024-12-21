from PySide2 import QtCore
from PySide2.QtCore import Qt, QMimeData
from PySide2.QtGui import QDrag, QIcon
from PySide2.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QAbstractItemView, \
    QPushButton, QHBoxLayout

from constants.constants import INTERNAL_MEMORY_USER_TONE_COUNT
from ui.loading_animation import LoadingAnimation
from utils.utils import resource_path
from utils.worker import Worker


class DragAndDropTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragged_item_row = None  # Store the row index of the dragged item
        self._row_offset = 801  # Start row numbering from 801
        self._setup_table()

    def _setup_table(self):
        """Setup the table configuration."""
        self.setColumnCount(1)  # One column for the user tone
        self.setHorizontalHeaderLabels(["User Tone"])  # Set the header label for the item column
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Prevent editing
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # Select entire rows
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        self.verticalHeader().setMinimumWidth(50)
        self.horizontalHeader().setStretchLastSection(True)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(item.text())  # Store the text of the item being dragged
            drag.setMimeData(mime_data)

            self._dragged_item_row = self.row(item)  # Track the dragged item's row
            drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            self._handle_drop(event)

    def _handle_drop(self, event):
        """Handles the drop event and rearranges the dragged item."""
        text = event.mimeData().text().strip()
        drop_row = self.rowAt(event.pos().y())  # Get the row where the item is dropped

        # Ensure the drop row is a valid row indexMy Drum
        drop_row = drop_row if drop_row != -1 and drop_row < self.rowCount() else self.rowCount() - 1

        # If the drop position is outside the table, do nothing
        if drop_row < 0 or drop_row >= self.rowCount():
            return

        item = self.takeItem(self._dragged_item_row, 0)  # Remove the item from its original position
        self.removeRow(self._dragged_item_row)  # Remove the row itself
        self.insertRow(drop_row)  # Insert the item at the new position
        self.setItem(drop_row, 0, item)  # Add the item to the new row

        # After the drop, update the row numbers starting from 801
        self._update_row_numbers()

        event.acceptProposedAction()

    def addItem(self, item_text, row=None):
        """Adds an item to a specified row, or at the end if no row is specified."""
        if row is None:
            row = self.rowCount()  # If no row specified, add to the end

        self.insertRow(row)  # Insert the row at the specified position
        self.setItem(row, 0, QTableWidgetItem(item_text))  # Add the item to the row

        # After adding a new item, update the row numbers starting from 801
        self._update_row_numbers()

    def itemExists(self, text):
        """Checks if an item with the given text already exists in the table."""
        return any(self.item(row, 0).text() == text for row in range(self.rowCount()))

    def _update_row_numbers(self):
        """Updates the row numbers in the vertical header starting from 801."""
        row_count = self.rowCount()
        row_labels = [str(self._row_offset + i) for i in range(row_count)]
        self.setVerticalHeaderLabels(row_labels)


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

        label = QLabel("Drag-and-Drop User Tone List. Buttons are not working.")
        label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(label)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)

        self.table_widget = DragAndDropTable(self)
        content_layout.addWidget(self.table_widget)

        self.refresh_button = QPushButton(" Refresh")
        self.refresh_button.setIcon(QIcon(resource_path("resources/refresh.png")))
        self.refresh_button.setObjectName("manager-button")
        self.refresh_button.clicked.connect(self.load_memory_tone_names)

        self.upload_button = QPushButton(" Save Tone")
        self.upload_button.setIcon(QIcon(resource_path("resources/piano_plus.png")))
        self.upload_button.setObjectName("manager-button")

        self.rename_button = QPushButton(" Rename")
        self.rename_button.setIcon(QIcon(resource_path("resources/piano_pencil.png")))
        self.rename_button.setObjectName("manager-button")

        self.delete_button = QPushButton(" Delete")
        self.delete_button.setIcon(QIcon(resource_path("resources/piano_minus.png")))
        self.delete_button.setObjectName("manager-button")

        self.apply_button = QPushButton(" Apply")
        self.apply_button.setIcon(QIcon(resource_path("resources/apply.png")))
        self.apply_button.setObjectName("manager-button")

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

        self.loading_animation.stop()

    def resizeEvent(self, event):
        super(UserToneManagerWindow, self).resizeEvent(event)
        self.loading_animation.center_loading_animation()
