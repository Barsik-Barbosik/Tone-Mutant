import os
import sys
import tempfile

from PySide2.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils.utils import resource_path

# Nuitka compiler options:
# nuitka-project: --output-filename=ToneMutant
# nuitka-project: --product-name=ToneMutant
# nuitka-project: --product-version=1.2.5
# nuitka-project: --file-version=1.2.5
# nuitka-project: --file-description="Tone editor for Casio keyboards"
# nuitka-project: --company-name="Barsik-Barbosik"
# nuitka-project: --standalone
# nuitka-project: --onefile
# nuitka-project: --onefile-windows-splash-screen-image={MAIN_DIRECTORY}/resources/splash.png
# nuitka-project: --enable-plugin=pyside2
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/resources=resources
# nuitka-project: --windows-icon-from-ico=resources/note.ico
# nuitka-project: --windows-console-mode=disable
# nuitka-project: --remove-output

if __name__ == '__main__':
    # Splash screen (Nuitka)
    if "NUITKA_ONEFILE_PARENT" in os.environ:
        splash_filename = os.path.join(
            tempfile.gettempdir(),
            "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
        )

        if os.path.exists(splash_filename):
            os.unlink(splash_filename)

    app = QApplication(sys.argv)

    with open(resource_path("resources/style.qss"), "r") as style_file:
        style = style_file.read()
        app.setStyleSheet(style)

    window = MainWindow()
    window.resize(1000, 600)
    window.show()

    app.aboutToQuit.connect(window.exit_call)
    sys.exit(app.exec_())
