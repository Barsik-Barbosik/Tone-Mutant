from PySide2.QtCore import Signal
from PySide2.QtWidgets import QListWidget


class InstrumentListWidget(QListWidget):
    setRowSignal = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._block_signal_temporarily = False

        # Connect the signal to the silent row-setting function
        self.setRowSignal.connect(self.set_current_row_silently)

    def set_current_row_from_thread(self, row):
        """Emit signal to schedule set_current_row_silently in the main thread."""
        self.setRowSignal.emit(row)  # Emit the signal with the row as argument

    def set_current_row_silently(self, row):
        """Set the current row without emitting signals."""
        self._block_signal_temporarily = True
        self.setCurrentRow(row)  # Set the row without emitting signals
        self._block_signal_temporarily = False

    def connect_signal(self, signal, slot):
        """Connect signals, ignoring them if temporary blocking is active."""

        def wrapped_slot(*args, **kwargs):
            if not self._block_signal_temporarily:
                slot(*args, **kwargs)

        signal.connect(wrapped_slot)
