from PySide2.QtCore import Qt, QRegExp
from PySide2.QtGui import QTextCharFormat, QSyntaxHighlighter


class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(JsonHighlighter, self).__init__(parent)

        rules = []

        # brackets
        # bracket_format = QTextCharFormat()
        # bracket_format.setForeground(Qt.darkCyan)
        # bracket_pattern = QRegExp(r'[\[\](){}<>]')
        # rules.append((bracket_pattern, bracket_format))

        # numbers, "null", "true", "false"
        number_format = QTextCharFormat()
        number_format.setForeground(Qt.blue)
        number_pattern = QRegExp(r'\b[0-9]+\b|null|[Tt]rue|[Ff]alse')
        rules.append((number_pattern, number_format))

        # names
        name_format = QTextCharFormat()
        name_format.setForeground(Qt.darkMagenta)
        name_pattern = QRegExp(r'"[^"]*"\s*')
        rules.append((name_pattern, name_format))

        # values
        value_format = QTextCharFormat()
        value_format.setForeground(Qt.darkGreen)
        value_pattern = QRegExp(r'\s*("[^"]*"|\.\d+)(?:,|$)')
        rules.append((value_pattern, value_format))

        self.highlighting_rules = [(QRegExp(pattern), format) for pattern, format in rules]

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)

            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
