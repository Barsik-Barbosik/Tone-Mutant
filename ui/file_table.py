from PySide2.QtCore import Qt, QMimeData
from PySide2.QtGui import QDrag
from PySide2.QtWidgets import QTableWidget, QAbstractItemView


class FileTable(QTableWidget):
    def __init__(self, parent=None, external_drag_drop_finished_callback=None):
        super().__init__(parent)
        self.external_drag_drop_finished_callback = external_drag_drop_finished_callback

        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(["File Name"])
        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setMinimumWidth(50)
        self.horizontalHeader().setStretchLastSection(True)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Prevent editing
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # Select entire rows
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        # self.setEditTriggers(QAbstractItemView.DoubleClicked)  # Allow editing on double click

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():  # Clicked on empty space
            self.clearSelection()  # Clear selection in file_table_widget
            if self.parent():  # Ensure parent exists before accessing
                self.parent().table_widget.clearSelection()  # Clear selection in table_widget
        super().mousePressEvent(event)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            mime_data = QMimeData()
            mime_data.setText(item.text())

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            if self == event.source():
                event.ignore()
            else:
                event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText() and event.source() != self and self.external_drag_drop_finished_callback:
            data = event.mimeData().text()  # String format: "row_number:item_text\nrow_number:item_text"
            rows_data = data.split("\n")  # Split by newline to get individual rows
            self.external_drag_drop_finished_callback(rows_data)
            event.acceptProposedAction()
