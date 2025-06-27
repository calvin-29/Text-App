from PyQt5.QtWidgets import (QApplication, QWidget, QTextEdit, QMainWindow, QMenuBar, QAction, QTabWidget, 
                             QVBoxLayout, QFileDialog, QMessageBox, QStatusBar, QLabel, QLineEdit, QHBoxLayout, 
                             QPushButton)
from PyQt5.QtGui import QIcon, QTextCursor
import sys, os

class TextApp(QMainWindow):
    fileopened = {} #index:file_path
    file_asterisk = False
    filesaved = {} #index:if_saved
    child_windows = []
    recent_files = set()
    def __init__(self):
        super().__init__()
        self.clip = QApplication.clipboard()
        self.setWindowTitle("Text App")
        self.setWindowIcon(QIcon(os.path.join(os.path.split(__file__)[0]+"/images","4.ico")))
        self.resize(1000, 600)
        self.initUI()

### method to initialize the widgets
    def initUI(self):
        self.window = QWidget()

        self.menu()
        self.status()

        self.tabs = QTabWidget(self.window)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_window)
        self.tabs.currentChanged.connect(self.get_row_column)
        vbox = QVBoxLayout(self.window)
        vbox.addWidget(self.tabs)
        self.initStyle()
        self.setCentralWidget(self.window)

#### method to add tabs
    def addNewTab(self, name, data=""):
        def changesave():
            self.filesaved[self.tabs.currentIndex()] = False
            self.file_asterisk = True
            self.asterisk()
        widget = QWidget()
        vbox2 = QVBoxLayout(widget)
        
        tab = QTextEdit(widget)

        tab.setText(data)
        tab.textChanged.connect(changesave)
        tab.setAcceptDrops(True)
        self.tabs.addTab(widget, QIcon(os.path.join(os.path.split(__file__)[0]+"/images","pyc.png")), name)
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
        vbox2.addWidget(tab)
        tab.cursorPositionChanged.connect(self.get_row_column)
        self.status()
        self.menu()

    def asterisk(self):
        if self.file_asterisk and not self.filesaved[self.tabs.currentIndex()]:
            index = self.tabs.currentIndex()
            if not self.tabs.tabText(index).startswith("*"):
                if index in self.fileopened:
                    self.tabs.setTabText(index, f"*{os.path.split(self.fileopened[self.tabs.currentIndex()])[1]}")
                else:
                    self.tabs.setTabText(index, "*New File")
        else:
            self.tabs.setTabText(self.tabs.currentIndex(), f"{os.path.split(self.fileopened[self.tabs.currentIndex()])[1]}")
            self.setWindowTitle(os.path.split(self.fileopened[self.tabs.currentIndex()])[1])

#### method to get current textedit
    def current_text_edit(self):
        return self.tabs.currentWidget().findChild(QTextEdit)

## double click event capture 
    def mouseDoubleClickEvent(self, a0):
        self.addNewTab("New File")

#### method to close window tab
    def close_window(self, tab=""):
        try:
            self.fileopened.pop(self.tabs.currentIndex())
        except KeyError:
            pass
        if tab == "":
            self.tabs.removeTab(self.tabs.currentIndex())
        else:
            self.tabs.removeTab(tab)
        if self.tabs.count() == 0:
            self.setWindowTitle("Text App")
        self.menu()
        self.status()

#### method to create menu bar
    def menu(self):
        menubar = QMenuBar()
        self.setMenuBar(menubar)

        # File Actions
        file = menubar.addMenu("File")
        file_commands = (["New", "Ctrl+N"], ["Save", "Ctrl+S"], ["Open", "Ctrl+O"], 
                         ["New Window", "Ctrl+Shift+N"], ["Close Tab", "Ctrl+W"], ["Quit", "Ctrl+Q"])
        for i in file_commands:
            action = QAction(i[0], self)
            action.setShortcut(i[1])
            file.addAction(action)
            if not hasattr(self, "tabs"):
                if action.text() == "Save" or action.text() == "Close Tab":
                    action.setEnabled(False)
            if i == ["Close Tab", "Ctrl+W"]:
                file.addSeparator()
                recent = file.addMenu("Recent Files")
                try:
                    with open(os.path.split(__file__)[0]+"/recent.lst", "r") as f:
                        for i in f.readlines():
                            recent.addAction(i)
                            self.recent_files.add(i)
                        if i == 0:
                            file.setEnabled(False)
                except FileNotFoundError:
                    with open("recent.lst", "w") as f:
                        pass
                recent.addSeparator()
                if len(self.recent_files) == 0:
                    recent.setEnabled(False)
                recent.addAction("Clear")
        # Edit Actions
        edit = menubar.addMenu("Edit")
        edit_commands = (["Copy", "Ctrl+C"], ["Paste", "Ctrl+V"], ["Find/Replace", "Ctrl+F"])
        for i in edit_commands:
            action = QAction(i[0], self)
            action.setShortcut(i[1])
            edit.addAction(action)
            if not hasattr(self, "tabs"):
                action.setEnabled(False)
        # Help Actions
        help = menubar.addMenu("Help")
        help_commands = ("Documentation", "About")
        for i in range(len(help_commands)):
            help.addAction(QAction(help_commands[i], self))

        menubar.triggered[QAction].connect(self.menu_commands)

#### method to create status bar
    def status(self, row=0, column=0):
        if hasattr(self, 'tabs'):
            self.statusbar = QStatusBar()
            self.setStatusBar(self.statusbar)
            self.status_label = QLabel()
            self.statusbar.addPermanentWidget(self.status_label, 0)
            self.status_label.setText(f"Ln {row}, Col {column}")

#### method to display row and column 
    def get_row_column(self):
        try:
            cursor = self.current_text_edit().textCursor()
            row = cursor.blockNumber()
            column = cursor.positionInBlock()
            self.status(row, column)
            self.setWindowTitle(f"{self.tabs.tabText(self.tabs.currentIndex())}")
        except Exception as e:
            pass

#### capture closing event
    def closeEvent(self, event):
        save = True
        for i in self.filesaved.values():
            if i == False:
                save = False
        if not save and self.tabs.count() != 0:
            reply = QMessageBox.question(self, "Closing", "There is still unsaved work\nAre you sure to quit?",
                             QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        
#### method to handle commands from the menu bar
    def menu_commands(self, command):
        command = command.text().lower()
        match command:
            case "new":
                self.addNewTab("New File")
            case "save":
                self.file("s")
            case "open":
                self.file("o")
            case "new window":
                new_win = TextApp()
                new_win.setGeometry(self.x()-10, self.y()+50, self.width(), self.height())
                new_win.show()
                self.child_windows.append(new_win)
            case "close tab":
                self.close_window()
            case "clear":
                with open(os.path.split(__file__)[0]+"/recent.lst", "w") as f:
                    f.write("")
                self.menu()
            case "quit":
                check = QMessageBox(QMessageBox.Question, "Exit", "Do you really want to exit", QMessageBox.Yes|QMessageBox.No)
                check.buttonClicked.connect(lambda e: self.close() if e.text() == "&Yes" else e.text())
                check.exec_()
            case "copy":
                if self.tabs.count() != 0:
                    self.clip.setText(self.current_text_edit().textCursor().selectedText())
            case "paste":
                if self.tabs.count() != 0:
                    cursor = self.current_text_edit().textCursor()
                    cursor.insertText(self.clip.text())
            case "find/replace":
                if self.tabs.count() != 0:
                    dlg = FindReplaceDialog(self)
                    dlg.show()
            case "documentation":
                QMessageBox.about(self, "Documentation",
                                  """
                                  Open the menu for commands and you can use shortcuts
                                  """)
            case "about":
                QMessageBox.about(self, "About", "Created in Nigeria by Calvin")
            case _:
                self.file("o", [1, command[:-1]])

#### method to add recent file
    def add_recent(self):
        try:
            path = os.path.split(__file__)[0]+"/recent.lst"
            # print(self.recent_files)
            with open(path, "r") as k:
                for j in k.readlines():
                    self.recent_files.add(f"{j}")
            with open(path, "w") as h:
                h.writelines(self.recent_files)
            self.menu()
        except FileNotFoundError:
            with open(path, "w") as h:
                pass

#### method to open and save file
    def file(self, file_handling, mode=[0,""]):
        if file_handling == "o":
            if mode[0] == 1:
                print(mode[1])
                if os.path.exists(mode[1]):
                    with open(mode[1], "r") as f:
                        # get filename name
                        filename_and_path = os.path.split(mode[1])
                        filename = filename_and_path[1]
                        # open a new tab and select that tab
                        self.addNewTab(filename, f.read())
                        self.tabs.setCurrentIndex(self.tabs.count()-1)
                        self.fileopened[self.tabs.currentIndex()] = mode[1]
                        self.filesaved[self.tabs.currentIndex()] = True
                        self.add_recent()
                else:
                    QMessageBox.warning(self, "Warning", "File is not found")

            else:
                while True:
                    file = QFileDialog.getOpenFileName(self, "Open File", os.path.split(__file__)[0], 
                                                    "All Files(* *.);;Text Files (*.txt);;Python Files (*.py *.pyw *.pyc)"
                                                    ,"Python Files (*.py *.pyw *.pyc)")
                    try:
                        if file[0] not in self.fileopened.values():
                            with open(file[0], "r") as f:
                                # get filename name
                                filename_and_path = os.path.split(file[0])
                                filename = filename_and_path[1]
                                # open a new tab and select that tab
                                self.addNewTab(filename, f.read())
                                self.tabs.setCurrentIndex(self.tabs.count()-1)
                                self.fileopened[self.tabs.currentIndex()] = file[0]
                                self.filesaved[self.tabs.currentIndex()] = True
                                self.recent_files.add(f"{file[0]}\n")
                                self.add_recent()
                        else:
                            for count, i in enumerate(self.fileopened.keys()):
                                if self.fileopened[count] == file[0]:
                                    self.tabs.setCurrentIndex(i)
                        break
                    except FileNotFoundError:
                        QMessageBox(QMessageBox.Critical, "No File", "No file was selected").exec_()
                        break
                    except UnicodeDecodeError:
                        QMessageBox(QMessageBox.Critical, "Unknown file type", "File type is unknown").exec_()
                        continue
        elif file_handling == "s":
            if self.tabs.count() > 0 and self.tabs.currentIndex() not in self.fileopened:
                file = QFileDialog.getSaveFileName(self, "Save File", os.path.split(__file__)[0], 
                                                "All Files(* *.);;Text Files (*.txt);;Python Files (*.py *.pyw *.pyc)"
                                                ,"Python Files (*.py *.pyw *.pyc)")
                try:
                    with open(file[0], "w") as f:
                        filename_and_path = os.path.split(file[0])
                        # get filename
                        self.filename = filename_and_path[1]
                        # create a file and write the content of the tab in it change the tab's text
                        f.write(self.current_text_edit().toPlainText())
                        self.tabs.setTabText(self.tabs.currentIndex(), self.filename)
                        self.setWindowTitle(f"{self.filename}")
                        self.fileopened[self.tabs.currentIndex()] = file[0]
                        self.filesaved[self.tabs.currentIndex()] = True
                        self.recent_files.add(f"{file[0]}\n")
                        self.add_recent()
                        self.menu()
                except FileNotFoundError:
                    QMessageBox(QMessageBox.Critical, "No File", "No file was selected").exec_()
                except Exception as e:
                    print(e)
            else:
                try:
                    with open(self.fileopened[self.tabs.currentIndex()], "w") as f:
                        f.write(self.current_text_edit().toPlainText())
                        self.filesaved[self.tabs.currentIndex()] = True
                        self.file_asterisk = False
                        self.asterisk()
                except Exception:
                    pass

#### method to style the widgets
    def initStyle(self):
        self.setStyleSheet(
            """
            *{
                font-size: 15px;
            }
            QStatusBar{
                background-color: rgb(200, 200, 200);
                color: white;
            }
            QTextEdit, QTabWidget{
                background-color: rgb(0, 36, 81);
                color: white;
                font-family: consolas;
                border-radius: 5px;
                padding: 10px;
            }
            QMessageBox{
                background-color: white;
            }
            QMainWindow {
                background-color: #001f3f;
            }
            """
        )

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

#### Main method to create the window
def main():
    app = QApplication(sys.argv)
    win = TextApp()
    win.show()
    if len(sys.argv) > 1:
        win.file("o", [1, sys.argv[1] ])
    app.exec_()

if __name__  == "__main__":
    main()
