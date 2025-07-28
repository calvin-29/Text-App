from editor import TextApp
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TextApp()
    win.show()
    if len(sys.argv) > 1:
        win.file("o", [1, sys.argv[1]])
    app.exec_()
