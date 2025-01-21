from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QIntValidator
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QMessageBox, \
    QHBoxLayout

from utils.utils import resource_path


class RequestParameterWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle("Request Parameter")
        self.setWindowIcon(QIcon(resource_path("resources/request.png")))

        self.core = parent.core

        layout = QVBoxLayout()

        title = QLabel()
        title.setText("<h2>Request a Parameter</h2>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Parameter Number...")
        self.number_input.setValidator(QIntValidator(0, 255, self))
        form_layout.addRow(self.create_colored_square_label("#0000FF", "Number:"), self.number_input)

        self.block0_input = QLineEdit()
        self.block0_input.setPlaceholderText("Block 0...")
        self.block0_input.setText("0")
        self.block0_input.setValidator(QIntValidator(0, 7, self))
        form_layout.addRow(self.create_colored_square_label("#FF00FF", "Block 0:"), self.block0_input)

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Category... (0-65)")
        self.category_input.setValidator(QIntValidator(0, 65, self))
        self.category_input.setText("3")
        form_layout.addRow(self.create_colored_square_label("#006400", "Category:"), self.category_input)

        self.memory_input = QLineEdit()
        self.memory_input.setPlaceholderText("Memory... (0-4)")
        self.memory_input.setValidator(QIntValidator(0, 4, self))
        self.memory_input.setText("3")
        form_layout.addRow(self.create_colored_square_label("#FF00FF", "Memory Area ID:"), self.memory_input)

        self.parameter_set_input = QLineEdit()
        self.parameter_set_input.setPlaceholderText("Parameter Set...")
        self.parameter_set_input.setValidator(QIntValidator(0, 1499, self))
        self.parameter_set_input.setText("0")
        form_layout.addRow(self.create_colored_square_label("#006400", "Parameter Set:"), self.parameter_set_input)

        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("Size...")
        self.size_input.setValidator(QIntValidator(0, 65535, self))
        self.size_input.setText("0")
        form_layout.addRow(self.create_colored_square_label("#0000FF", "Size:"), self.size_input)

        layout.addLayout(form_layout)

        label = QLabel("The result will appear in the 'Log' tab.")
        label.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(label)

        self.submit_button = QPushButton(" Get Parameter!")
        self.submit_button.setIcon(QIcon(resource_path("resources/apply.png")))
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setFixedWidth(150)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        button_layout.addStretch()
        button_layout.setContentsMargins(10, 5, 10, 5)  # (left, top, right, bottom) margins

        layout.addLayout(button_layout)

        self.resize(330, 300)
        self.setLayout(layout)
        self.show()

    def on_submit(self):
        try:
            self.core.main_window.right_tab_widget.setCurrentIndex(1)  # open Log tab
            number = int(self.number_input.text())
            block0 = int(self.block0_input.text())
            category = int(self.category_input.text())
            memory = int(self.memory_input.text())
            parameter_set = int(self.parameter_set_input.text())
            size = int(self.size_input.text())
            self.core.request_custom_parameter(number, block0, category, memory, parameter_set, size)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "All fields must contain valid integers.")
            return

    @staticmethod
    def create_colored_square_label(color: str, text: str) -> QWidget:
        """
        Creates a widget containing a colored square and a label.

        Args:
            color (str): The color of the square (e.g., "red", "#ff0000").
            text (str): The text for the label.

        Returns:
            QWidget: A widget containing the colored square and label.
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)  # Space between square and text

        # Create the square label
        square_label = QLabel("⬛")  # Unicode black square
        square_label.setStyleSheet(f"color: {color};")  # Apply the color

        # Create the text label
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignVCenter)  # Align text vertically

        # Add both labels to the layout
        layout.addWidget(square_label)
        layout.addWidget(text_label)

        return container
