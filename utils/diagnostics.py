"""Retain Python, Qt and native crash diagnostics for the desktop executable."""
import faulthandler
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

_native_log = None
_qt_handler = None


def configure_logging():
    global _native_log, _qt_handler
    directory = Path("registros")
    directory.mkdir(exist_ok=True)
    logger = logging.getLogger("tone_mutant")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(directory / "aplicacion.log", maxBytes=1_000_000,
                                  backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(threadName)s %(message)s"))
    logger.addHandler(handler)
    _native_log = (directory / "fallos-nativos.log").open("a", encoding="utf-8")
    faulthandler.enable(_native_log, all_threads=True)

    def exception_hook(kind, value, trace):
        logger.critical("Excepción no controlada", exc_info=(kind, value, trace))
        if sys.stderr is not None:
            sys.__excepthook__(kind, value, trace)

    sys.excepthook = exception_hook
    from PySide6.QtCore import qInstallMessageHandler

    def qt_handler(kind, context, message):
        logger.warning("Qt: %s", message)

    _qt_handler = qt_handler
    qInstallMessageHandler(_qt_handler)
    logger.info("Inicio de Tone Mutant; Python %s", sys.version.split()[0])
