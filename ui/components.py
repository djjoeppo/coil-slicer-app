# ui/components.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from ui.viewer_3d import Coil3DViewer

class Dummy3DViewer(Coil3DViewer):
    def __init__(self, parent=None):
        super().__init__()

class GCodeHighlighter(QSyntaxHighlighter):
    """Industrial-grade QSyntaxHighlighter for G-code and M-code formatting."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlighting_rules = []

        # 1. Motion Commands (G0, G1, G28, G4)
        fmt_g = QTextCharFormat()
        fmt_g.setForeground(QColor("#00d2ff"))
        fmt_g.setFontWeight(QFont.Bold)
        rule_g = (QRegularExpression(r"\bG\d+\b", QRegularExpression.CaseInsensitiveOption), fmt_g)
        self.highlighting_rules.append(rule_g)

        # 2. Machine Commands (M0, M30, M400, M401, M402, M403)
        fmt_m = QTextCharFormat()
        fmt_m.setForeground(QColor("#ff9800"))
        fmt_m.setFontWeight(QFont.Bold)
        rule_m = (QRegularExpression(r"\bM\d+\b", QRegularExpression.CaseInsensitiveOption), fmt_m)
        self.highlighting_rules.append(rule_m)

        # 3. Axis Letters & Parameters (A, X, Y, Z, F, P)
        fmt_axis = QTextCharFormat()
        fmt_axis.setForeground(QColor("#00e676"))
        fmt_axis.setFontWeight(QFont.Bold)
        rule_axis = (QRegularExpression(r"\b[AXYZFPR]\b", QRegularExpression.CaseInsensitiveOption), fmt_axis)
        self.highlighting_rules.append(rule_axis)

        # 4. Numbers and Values
        fmt_num = QTextCharFormat()
        fmt_num.setForeground(QColor("#ffea00"))
        rule_num = (QRegularExpression(r"-?\d+(?:\.\d+)?"), fmt_num)
        self.highlighting_rules.append(rule_num)

        # 5. Comments (; ... or (...) )
        fmt_comment = QTextCharFormat()
        fmt_comment.setForeground(QColor("#78909c"))
        fmt_comment.setFontItalic(True)
        rule_comment1 = (QRegularExpression(r";.*"), fmt_comment)
        rule_comment2 = (QRegularExpression(r"\(.*?\)", QRegularExpression.CaseInsensitiveOption), fmt_comment)
        self.highlighting_rules.append(rule_comment1)
        self.highlighting_rules.append(rule_comment2)

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
