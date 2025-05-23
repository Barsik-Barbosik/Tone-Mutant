from PySide2.QtCore import Qt, QRegExp
from PySide2.QtGui import QTextCharFormat, QSyntaxHighlighter


class SysexHighlighter(QSyntaxHighlighter):
    HEX_COLORS = {
        # sysex first byte F0 is red
        1: {'foreground': Qt.gray, 'background': Qt.white},  # casio & model
        2: {'foreground': Qt.gray, 'background': Qt.white},  # casio & model
        3: {'foreground': Qt.gray, 'background': Qt.white},  # casio & model
        4: {'foreground': Qt.gray, 'background': Qt.white},  # casio & model
        5: {'foreground': Qt.red, 'background': Qt.white},  # action
        6: {'foreground': Qt.darkGreen, 'background': Qt.white},  # category
        7: {'foreground': Qt.magenta, 'background': Qt.white},  # memory area id
        8: {'foreground': Qt.darkGreen, 'background': Qt.white},  # parameter set
        9: {'foreground': Qt.darkGreen, 'background': Qt.white},  # parameter set
        10: {'foreground': Qt.gray, 'background': Qt.white},  # block 3
        11: {'foreground': Qt.gray, 'background': Qt.white},  # block 3
        12: {'foreground': Qt.gray, 'background': Qt.white},  # block 2
        13: {'foreground': Qt.gray, 'background': Qt.white},  # block 2
        14: {'foreground': Qt.gray, 'background': Qt.white},  # block 1
        15: {'foreground': Qt.gray, 'background': Qt.white},  # block 1
        16: {'foreground': Qt.magenta, 'background': Qt.white},  # block 0
        17: {'foreground': Qt.magenta, 'background': Qt.white},  # block 0
        18: {'foreground': Qt.blue, 'background': Qt.white},  # param number
        19: {'foreground': Qt.blue, 'background': Qt.white},  # param number
        20: {'foreground': Qt.gray, 'background': Qt.white},  # data index number
        21: {'foreground': Qt.gray, 'background': Qt.white},  # data index number
        22: {'foreground': Qt.blue, 'background': Qt.white},  # size
        23: {'foreground': Qt.blue, 'background': Qt.white}  # size
        # request/response data symbols are black
        # sysex last byte F7 is red
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.word_formats = self._create_word_formats()
        self.word_regex = QRegExp(r'\b\w+\b')

    def _create_word_formats(self):
        """Create and return a list of word index and QTextCharFormat pairs."""
        return [
            (word_index, self._create_text_format(styles))
            for word_index, styles in self.HEX_COLORS.items()
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
