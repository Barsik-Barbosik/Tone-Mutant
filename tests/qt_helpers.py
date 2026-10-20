def synchronize_tone_with_synth(self):
    """Use a real bound Python method as a Qt slot; MagicMock is not a Qt receiver."""
    self._test_synchronizations = getattr(self, "_test_synchronizations", 0) + 1
