from PySide2.QtWidgets import QTableWidget


class FileTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(["File Name"])
        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setMinimumWidth(50)
        self.horizontalHeader().setStretchLastSection(True)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():  # Clicked on empty space
            self.clearSelection()  # Clear selection in file_table_widget
            if self.parent():  # Ensure parent exists before accessing
                self.parent().table_widget.clearSelection()  # Clear selection in table_widget
        super().mousePressEvent(event)
