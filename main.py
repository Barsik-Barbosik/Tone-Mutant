import os
import sys
import tempfile

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils.utils import resource_path
from ui.i18n import install_qt_spanish

# Nuitka compiler options:
# nuitka-project: --output-filename=ToneMutant
# nuitka-project: --product-name=ToneMutant
# nuitka-project: --product-version=1.3.3
# nuitka-project: --file-version=1.3.3
# nuitka-project: --file-description="Tone editor for Casio keyboards"
# nuitka-project: --company-name="Barsik-Barbosik"
# nuitka-project: --standalone
# nuitka-project: --onefile
# nuitka-project: --onefile-windows-splash-screen-image={MAIN_DIRECTORY}/resources/splash.png
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/resources=resources
# nuitka-project: --windows-icon-from-ico=resources/note.ico
# nuitka-project: --windows-console-mode=disable
# nuitka-project: --remove-output

if __name__ == '__main__':
    if "--self-test" in sys.argv:
        from tools.selftest_runtime import run_selftest
        index = sys.argv.index("--self-test")
        sys.exit(run_selftest(sys.argv[index + 1]))
    if getattr(sys, "frozen", False):
        os.chdir(os.path.dirname(sys.executable))
    from utils.diagnostics import configure_logging
    configure_logging()
    # Splash screen (Nuitka)
    if "NUITKA_ONEFILE_PARENT" in os.environ:
        splash_filename = os.path.join(
            tempfile.gettempdir(),
            "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
        )

        if os.path.exists(splash_filename):
            os.unlink(splash_filename)

    app = QApplication(sys.argv)
    app.setApplicationName("Tone Mutant")
    install_qt_spanish(app)

    with open(resource_path("resources/style.qss"), "r") as style_file:
        style = style_file.read()
        app.setStyleSheet(style)

    window = MainWindow()
    window.resize(1280, 800)
    window.show()

    app.aboutToQuit.connect(window.exit_call)
    sys.exit(app.exec())
