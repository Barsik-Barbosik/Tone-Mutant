from PySide2.QtCore import Qt, QMimeData
from PySide2.QtGui import QDrag
from PySide2.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, QItemDelegate


class LimitedLengthEditor(QLineEdit):
    def __init__(self, parent=None, max_length=8):
        super().__init__(parent)
        self.setMaxLength(max_length)  # Set the max length of input


class LimitedLengthDelegate(QItemDelegate):
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.callback = callback  # Store the callback function passed as a parameter

    def createEditor(self, parent, option, index):
        # Create a custom QLineEdit editor with a max length of 8
        editor = LimitedLengthEditor(parent, max_length=8)

        # If a callback is provided, connect the `editingFinished` signal to it
        if self.callback:
            editor.editingFinished.connect(self.callback)

        return editor


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
        # self.setDragDropMode(QTableWidget.InternalMove)
        # self.setAlternatingRowColors(True)
        # self.setEditTriggers(QAbstractItemView.DoubleClicked)  # Allow editing on double click
        # self.setItemDelegateForColumn(0, LimitedLengthDelegate(self))
        self.setItemDelegateForColumn(0, LimitedLengthDelegate(self, callback=self.abc))

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

    # def currentRowWithOffset(self):
    #     """Returns the row index considering the row offset."""
    #     # Get the current row, then subtract the offset to adjust the row number
    #     current_row = self.currentRow()
    #     if current_row == -1:
    #         return -1
    #     return current_row + self._row_offset - 1  # Adjust for 0-based index

    def keyPressEvent(self, event):
        # Check if the pressed key is Enter
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Disable the default behavior for Enter key
            return
        # Call the parent class' keyPressEvent for all other keys
        super().keyPressEvent(event)

    def abc(self):
        print("Hello??")
