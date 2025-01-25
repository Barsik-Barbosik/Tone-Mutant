from PySide2.QtWidgets import QFileDialog


class FileDialogHelper:
    @staticmethod
    def open_json_dialog(parent):
        """
        Opens a file dialog to select a JSON file for reading.
        :param parent: The parent widget for the dialog.
        :return: The selected file path as a string or None if no file is selected.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            parent,
            "Open JSON File",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        return file_name if file_name else None

    @staticmethod
    def save_json_dialog(parent, default_filename=""):
        """
        Opens a file dialog to select a location to save a JSON file.
        :param parent: The parent widget for the dialog.
        :param default_filename: The default file name for the dialog.
        :return: The selected file path as a string or None if no file is selected.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            parent,
            "Save JSON File",
            default_filename,
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        return file_name if file_name else None

    @staticmethod
    def save_ton_dialog(parent, default_filename=""):
        """
        Opens a file dialog to select a location to save a TON file.
        :param parent: The parent widget for the dialog.
        :param default_filename: The default file name for the dialog.
        :return: The selected file path as a string or None if no file is selected.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            parent,
            "Save TON File",
            default_filename,
            "TON Files (*.ton);;All Files (*)",
            options=options
        )
        return file_name if file_name else None
