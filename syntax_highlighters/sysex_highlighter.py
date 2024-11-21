from PySide2.QtCore import Qt, QRegExp
from PySide2.QtGui import QTextCharFormat, QSyntaxHighlighter


class SysexHighlighter(QSyntaxHighlighter):
    WORD_STYLES = {
        1: {'foreground': Qt.darkGreen, 'background': Qt.white},
        2: {'foreground': Qt.darkGreen, 'background': Qt.white},
        3: {'foreground': Qt.darkGreen, 'background': Qt.white},
        4: {'foreground': Qt.darkGreen, 'background': Qt.white},
        5: {'foreground': Qt.magenta, 'background': Qt.white},
        6: {'foreground': Qt.darkGreen, 'background': Qt.white},
        7: {'foreground': Qt.darkGreen, 'background': Qt.white},
        16: {'foreground': Qt.magenta, 'background': Qt.white},
        17: {'foreground': Qt.magenta, 'background': Qt.white},
        18: {'foreground': Qt.blue, 'background': Qt.white},
        19: {'foreground': Qt.blue, 'background': Qt.white},
        22: {'foreground': Qt.magenta, 'background': Qt.white},
        23: {'foreground': Qt.magenta, 'background': Qt.white},
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.word_formats = self._create_word_formats()
        self.word_regex = QRegExp(r'\b\w+\b')

    def _create_word_formats(self):
        """Create and return a list of word index and QTextCharFormat pairs."""
        return [
            (word_index, self._create_text_format(styles))
            for word_index, styles in self.WORD_STYLES.items()
        ]

    @staticmethod
    def _create_text_format(styles):
        """Create a QTextCharFormat object with given styles."""
        text_format = QTextCharFormat()
        text_format.setForeground(styles['foreground'])
        text_format.setBackground(styles['background'])
        return text_format

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        self._highlight_word_styles(text)
        self._highlight_bracketed_text(text)
        self._highlight_keywords(text, r'F0|F7', Qt.red)
        self._highlight_prefixed_line(text, "[INFO]", Qt.darkGray)
        self._highlight_prefixed_line(text, "[ERROR]", Qt.red)

    def _highlight_word_styles(self, text):
        """Highlight words based on predefined styles."""
        space_positions = self._find_space_positions(text)
        for word_index, word_format in self.word_formats:
            if word_index < len(space_positions):
                start_pos = space_positions[word_index] + 1 if space_positions[word_index] > 0 else 0
                char_count = (
                    space_positions[word_index + 1] - start_pos
                    if word_index + 1 < len(space_positions)
                    else len(text) - start_pos
                )
                self.setFormat(start_pos, char_count, word_format)

    def _highlight_bracketed_text(self, text):
        """Highlight text within brackets."""
        if "]" in text:
            try:
                bracket_position = text.index("]")
                self.setFormat(0, bracket_position + 1, Qt.darkMagenta)
                self.setFormat(bracket_position + 1, len(text) - bracket_position - 1, Qt.blue)
            except ValueError:
                pass

    def _highlight_keywords(self, text, pattern, color):
        """Highlight keywords matching the given pattern."""
        expression = QRegExp(pattern)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(color)

        index = expression.indexIn(text)
        while index >= 0:
            length = expression.matchedLength()
            self.setFormat(index, length, keyword_format)
            index = expression.indexIn(text, index + length)

    def _highlight_prefixed_line(self, text, prefix, color):
        """Highlight lines starting with a specific prefix."""
        if text.startswith(prefix):
            line_format = QTextCharFormat()
            line_format.setForeground(color)
            self.setFormat(0, len(text), line_format)

    @staticmethod
    def _find_space_positions(text):
        """Find and return the positions of spaces in the text."""
        positions = [0]
        index = -1
        while True:
            try:
                index = text.index(" ", index + 1)
                if index > 0 and text[index - 1] == " ":
                    continue
                positions.append(index)
            except ValueError:
                break
        return positions
