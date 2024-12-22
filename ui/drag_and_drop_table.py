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
        self.callback = callback
        self.value_before_edit = None

    def createEditor(self, parent, option, index):
        editor = LimitedLengthEditor(parent, max_length=8)
        self.value_before_edit = index.data(Qt.EditRole)
        return editor

    def setModelData(self, editor, model, index):
        new_value = editor.text()
        model.setData(index, new_value, Qt.EditRole)  # Update the model

        # Trigger the callback only if the value has changed
        if self.callback and self.value_before_edit != new_value:
            self.callback()


class DragAndDropTable(QTableWidget):
    def __init__(self, parent=None, table_row_offset=0, editing_finished_callback=None):
        super().__init__(parent)
        self._dragged_item_row = None  # Store the row index of the dragged item
        self._row_offset = table_row_offset  # Start row numbering from offset (801 for user tones)
        self.editing_finished_callback = editing_finished_callback  # Store the callback
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
        self.setEditTriggers(QAbstractItemView.DoubleClicked)  # Allow editing on double click
        self.setItemDelegateForColumn(0, LimitedLengthDelegate(self, callback=self.editing_finished_callback))

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

        # Ensure the drop row is a valid row index
        drop_row = drop_row if drop_row != -1 and drop_row < self.rowCount() else self.rowCount() - 1

        # If the drop position is outside the table, do nothing
        if drop_row < 0 or drop_row >= self.rowCount():
            return

        item = self.takeItem(self._dragged_item_row, 0)  # Remove the item from its original position
        self.removeRow(self._dragged_item_row)  # Remove the row itself
        self.insertRow(drop_row)  # Insert the item at the new position
        self.setItem(drop_row, 0, item)  # Add the item to the new row

        # After the drop, update the row numbers starting from table_row_offset
        self._update_row_numbers()

        event.acceptProposedAction()

    def addItem(self, item_text, row=None):
        """Adds an item to a specified row, or at the end if no row is specified."""
        if row is None:
            row = self.rowCount()  # If no row specified, add to the end

        self.insertRow(row)  # Insert the row at the specified position
        self.setItem(row, 0, QTableWidgetItem(item_text))  # Add the item to the row

        # After adding a new item, update the row numbers starting from table_row_offset
        self._update_row_numbers()

    def itemExists(self, text):
        """Checks if an item with the given text already exists in the table."""
        return any(self.item(row, 0).text() == text for row in range(self.rowCount()))

    def _update_row_numbers(self):
        """Updates the row numbers in the vertical header starting from table_row_offset."""
        row_count = self.rowCount()
        row_labels = [str(self._row_offset + i) for i in range(row_count)]
        self.setVerticalHeaderLabels(row_labels)

    def keyPressEvent(self, event):
        # Check if the pressed key is Enter
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Disable the default behavior for Enter key
            return
        # Call the parent class' keyPressEvent for all other keys
        super().keyPressEvent(event)
