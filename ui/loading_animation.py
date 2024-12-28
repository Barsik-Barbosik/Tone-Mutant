from PySide2.QtCore import Qt
from PySide2.QtGui import QMovie
from PySide2.QtWidgets import QLabel, QVBoxLayout, QWidget, QApplication

from utils.utils import resource_path


class LoadingAnimation(QWidget):
    def __init__(self, parent):
        super(LoadingAnimation, self).__init__(parent)

        self.setFixedSize(200, 200)

        # Initialize Layout
        self.layout = QVBoxLayout(self)
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)

        # Configure the GIF
        self.movie = QMovie(resource_path("resources/loading.gif"))
        self.loading_label.setMovie(self.movie)
        self.layout.addWidget(self.loading_label)

        self.setVisible(False)  # Hidden by default

    def start(self):
        """Start the loading animation and make it visible."""
        self.center_loading_animation()
        self.setVisible(True)
        self.movie.start()
        self.raise_()
        QApplication.processEvents()

    def stop(self):
        """Stop the loading animation and hide it."""
        self.movie.stop()
        self.setVisible(False)

    def center_loading_animation(self):
        """Position the loading animation widget in the center of the main window."""
        # if self.isVisible():
        parent_size = self.parent().size()  # Get the parent size (MainWindow size)
        widget_size = self.size()  # Get the loading animation widget size

        # Calculate the position to center the widget in the parent window
        x = (parent_size.width() - widget_size.width()) // 2
        y = (parent_size.height() - widget_size.height()) // 2

        # Move the loading widget to the center
        self.move(x, y)
