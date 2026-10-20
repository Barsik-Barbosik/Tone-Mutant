from ui.i18n import tr
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QIntValidator
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QMessageBox, \
    QHBoxLayout

from utils.utils import resource_path
from ui.accessibility import enable_escape_to_close


class RequestParameterWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        enable_escape_to_close(self)

        self.setWindowTitle(tr("Request Parameter"))
        self.setWindowIcon(QIcon(resource_path("resources/request.png")))

        self.core = parent.core

        layout = QVBoxLayout()

        title = QLabel()
        title.setText(tr("<h2>Request a Parameter</h2>"))
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText(tr("Parameter Number..."))
        self.number_input.setValidator(QIntValidator(0, 255, self))
        form_layout.addRow(self.create_colored_square_label("#0000FF", "Number:"), self.number_input)

        self.block0_input = QLineEdit()
        self.block0_input.setPlaceholderText(tr("Block 0..."))
        self.block0_input.setText(tr("0"))
        self.block0_input.setValidator(QIntValidator(0, 7, self))
        form_layout.addRow(self.create_colored_square_label("#FF00FF", "Block 0:"), self.block0_input)

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText(tr("Category... (0-65)"))
        self.category_input.setValidator(QIntValidator(0, 65, self))
        self.category_input.setText(tr("3"))
        form_layout.addRow(self.create_colored_square_label("#006400", "Category:"), self.category_input)

        self.memory_input = QLineEdit()
        self.memory_input.setPlaceholderText(tr("Memory... (0-4)"))
        self.memory_input.setValidator(QIntValidator(0, 4, self))
        self.memory_input.setText(tr("3"))
        form_layout.addRow(self.create_colored_square_label("#FF00FF", "Memory Area ID:"), self.memory_input)

        self.parameter_set_input = QLineEdit()
        self.parameter_set_input.setPlaceholderText(tr("Parameter Set..."))
        self.parameter_set_input.setValidator(QIntValidator(0, 1499, self))
        self.parameter_set_input.setText(tr("0"))
        form_layout.addRow(self.create_colored_square_label("#006400", "Parameter Set:"), self.parameter_set_input)

        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText(tr("Size..."))
        self.size_input.setValidator(QIntValidator(0, 16383, self))
        self.size_input.setText(tr("0"))
        form_layout.addRow(self.create_colored_square_label("#0000FF", "Size:"), self.size_input)

        layout.addLayout(form_layout)

        for field, name in [
            (self.number_input, "Parameter Number"),
            (self.block0_input, "Block 0"),
            (self.category_input, "Category"),
            (self.memory_input, "Memory Area ID"),
            (self.parameter_set_input, "Parameter Set"),
            (self.size_input, "Size"),
        ]:
            field.setAccessibleName(tr(name))
            validator = field.validator()
            field.setAccessibleDescription("Número entero de {} a {}.".format(validator.bottom(), validator.top()))

        label = QLabel(tr("The result will appear in the 'Log' tab."))
        label.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(label)

        self.submit_button = QPushButton(tr(" Get Parameter!"))
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
        for field in (self.number_input, self.block0_input, self.category_input,
                      self.memory_input, self.parameter_set_input, self.size_input):
            if not field.hasAcceptableInput():
                QMessageBox.warning(self, tr("Input Error"),
                                    tr("Check the value for " + field.accessibleName() + ". " +
                                    field.accessibleDescription()))
                field.setFocus()
                return
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
            QMessageBox.warning(self, tr("Input Error"), tr("All fields must contain valid integers."))
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
        square_label = QLabel(tr("⬛"))  # Unicode black square
        square_label.setStyleSheet(f"color: {color};")  # Apply the color

        # Create the text label
        text_label = QLabel(tr(text))
        text_label.setAlignment(Qt.AlignVCenter)  # Align text vertically

        # Add both labels to the layout
        layout.addWidget(square_label)
        layout.addWidget(text_label)

        return container
