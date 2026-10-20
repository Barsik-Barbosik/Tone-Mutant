from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QTextCharFormat, QSyntaxHighlighter


class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(JsonHighlighter, self).__init__(parent)

        rules = []

        # brackets
        # bracket_format = QTextCharFormat()
        # bracket_format.setForeground(Qt.darkCyan)
        # bracket_pattern = QRegularExpression(r'[\[\](){}<>]')
        # rules.append((bracket_pattern, bracket_format))

        # numbers, "null", "true", "false"
        number_format = QTextCharFormat()
        number_format.setForeground(Qt.blue)
        number_pattern = QRegularExpression(r'\b[0-9]+\b|null|[Tt]rue|[Ff]alse')
        rules.append((number_pattern, number_format))

        # names
        name_format = QTextCharFormat()
        name_format.setForeground(Qt.darkMagenta)
        name_pattern = QRegularExpression(r'"[^"]*"\s*')
        rules.append((name_pattern, name_format))

        # values
        value_format = QTextCharFormat()
        value_format.setForeground(Qt.darkGreen)
        value_pattern = QRegularExpression(r'\s*("[^"]*"|\.\d+)(?:,|$)')
        rules.append((value_pattern, value_format))

        self.highlighting_rules = [(QRegularExpression(pattern), format) for pattern, format in rules]

    def highlightBlock(self, text):
        for expression, text_format in self.highlighting_rules:
            matches = expression.globalMatch(text)
            while matches.hasNext():
                match = matches.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), text_format)
