# import neccesary modules
from PyQt5.QtWidgets import (QWidget, QTextEdit, QMainWindow, QVBoxLayout, QMessageBox, QLabel, QLineEdit, QHBoxLayout, 
                             QPushButton)
from PyQt5.QtGui import QTextCursor, QMouseEvent, QTextOption
from PyQt5.QtCore import Qt, pyqtSignal

class ClickLabel(QLabel):
    clicked = pyqtSignal(str)
    def __init__(self):
        super().__init__()
    
    def mousePressEvent(self, ev: QMouseEvent):
        if ev.button() == Qt.LeftButton:
            self.clicked.emit(self.text())
        return super().mousePressEvent(ev)

# text editor class
class TextEditor(QTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWordWrapMode(QTextOption.NoWrap)

    # capture key events
    def keyPressEvent(self, event):
        cursor = self.textCursor()
        current_block_text = cursor.block().text()

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Get indentation of current line
            leading_whitespace = self.get_leading_whitespace(current_block_text)
        
            super().keyPressEvent(event)
            if current_block_text.rstrip().endswith(":"):
                # Insert new line with same indentation
                cursor.insertText(leading_whitespace + "   ")
            elif current_block_text.rstrip().endswith("{"):
                # Insert new line with same indentation
                cursor.insertText(leading_whitespace + "   ")
            else:
                # Insert new line with same indentation
                cursor.insertText(leading_whitespace)
        else:
            super().keyPressEvent(event)

    def get_leading_whitespace(self, text):
        #Subtract stripped text from normal text 
        return text[:len(text) - len(text.lstrip())]

    def setText(self, text):
        self.textCursor().insertText(text)


class FindReplaceDialog(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setFixedSize(400, 150)
        self.setStyleSheet("QMainWindow, QMessageBox{background-color:rgb(50, 50, 50)}QLabel{color:rgb(200, 200, 200)}")

        self.parent = parent

        window = QWidget()

        self.find_input = QLineEdit()
        self.replace_input = QLineEdit()
        self.find_btn = QPushButton("Find")
        self.replace_btn = QPushButton("Replace")
        self.replace_all_btn = QPushButton("Replace All")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Find:"))
        layout.addWidget(self.find_input)
        layout.addWidget(QLabel("Replace With:"))
        layout.addWidget(self.replace_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.find_btn)
        btn_layout.addWidget(self.replace_btn)
        btn_layout.addWidget(self.replace_all_btn)

        layout.addLayout(btn_layout)
        window.setLayout(layout)

        self.find_btn.clicked.connect(self.find)
        self.replace_btn.clicked.connect(self.replace)
        self.replace_all_btn.clicked.connect(self.replace_all)

        self.setCentralWidget(window)

    def get_editor(self):
        return self.parent.tabs.currentWidget().findChild(QTextEdit)

    def find(self):
        editor = self.get_editor()
        cursor = editor.textCursor()
        text_to_find = self.find_input.text()
        
        for j in range(editor.toPlainText().count(text_to_find)): 
            if editor.toPlainText().find(text_to_find) != -1:
                start_position = editor.toPlainText().find(text_to_find)
                end_position = start_position + len(text_to_find)

                cursor.setPosition(start_position)
                cursor.setPosition(end_position, QTextCursor.MoveMode.KeepAnchor)
                editor.setTextCursor(cursor)
            else:
                QMessageBox.information(self, "Not Found", f"'{text_to_find}' not found.")

    def replace(self):
        editor = self.get_editor()
        cursor = editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
        else:
            self.find()

    def replace_all(self):
        editor = self.get_editor()
        content = editor.toPlainText()
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        count = content.count(find_text)
        if count == 0:
            QMessageBox.information(self, "No Matches", "No matches found.")
            return
        editor.setPlainText(content.replace(find_text, replace_text))
        QMessageBox.information(self, "Replace All", f"Replaced {count} occurrence(s).")
