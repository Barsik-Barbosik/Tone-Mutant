from PySide2.QtCore import Qt, QRegExp
from PySide2.QtGui import QTextCharFormat, QSyntaxHighlighter


class SysexHighlighter(QSyntaxHighlighter):
    WORD_STYLES = {
        1: {'foreground': Qt.darkGreen, 'background': Qt.white},
        2: {'foreground': Qt.darkGreen, 'background': Qt.white},
        3: {'foreground': Qt.darkGreen, 'background': Qt.white},
        4: {'foreground': Qt.darkGreen, 'background': Qt.white},
        5: {'foreground': Qt.darkGreen, 'background': Qt.white},
        6: {'foreground': Qt.darkGreen, 'background': Qt.white},
        7: {'foreground': Qt.darkGreen, 'background': Qt.white},
        16: {'foreground': Qt.black, 'background': Qt.yellow},
        18: {'foreground': Qt.black, 'background': Qt.yellow},
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.word_formats = self.create_word_formats()
        self.wordRegExp = QRegExp(r'\b\w+\b')

    def create_word_formats(self):
        formats = []
        for wordIndex, styles in self.WORD_STYLES.items():
            word_format = QTextCharFormat()
            word_format.setForeground(styles['foreground'])
            word_format.setBackground(styles['background'])
            formats.append((wordIndex, word_format))
        return formats

    def highlightBlock(self, text):
        self.highlight_word_styles(text)
        self.highlight_keywords(text, r'MIDI OUT:|MIDI IN:', Qt.darkMagenta)
        self.highlight_keywords(text, r'F0|F7', Qt.red)

    def highlight_word_styles(self, text):
        space_positions = self.find_space_positions(text)
        for word_index, word_format in self.word_formats:
            if word_index < len(space_positions):
                start_pos = space_positions[word_index] + 1 if space_positions[word_index] > 0 else 0
                char_count = space_positions[word_index + 1] - start_pos if word_index + 1 < len(
                    space_positions) else len(text) - start_pos
                self.setFormat(start_pos, char_count, word_format)

    def highlight_keywords(self, text, pattern, color):
        expression = QRegExp(pattern)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(color)
        index = expression.indexIn(text)

        while index >= 0:
            length = expression.matchedLength()
            self.setFormat(index, length, keyword_format)
            index = expression.indexIn(text, index + length)

    @staticmethod
    def find_space_positions(string):
        positions = [0]
        index = -1
        while True:
            try:
                index = string.index(" ", index + 1)
                if index - 1 >= 0 and string[index - 1] == " ":
                    continue
                positions.append(index)
            except ValueError:
                break
        return positions
