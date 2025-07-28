from PyQt5.QtWidgets import (QApplication, QWidget, QTextEdit, QMainWindow, QMenuBar, QAction, QTabWidget, 
                             QVBoxLayout, QFileDialog, QMessageBox, QStatusBar, QLabel, QHBoxLayout, QSplitter, 
                             QScrollArea, QFileSystemModel, QTreeView)
from PyQt5.QtGui import QIcon, QPixmap, QTransform
from PyQt5.QtCore import Qt, QDir, QTimer
import os, html
from file_utils import TextEditor, FindReplaceDialog

# main app class
class TextApp(QMainWindow):
    child_windows = []
    recent_files = []
    folder = ""
    save_directory = os.path.join(QDir.homePath(), "AppData", "Roaming", "XDS")
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    def __init__(self):
        super().__init__()
        # set window properties
        self.clip = QApplication.clipboard()
        self.setWindowTitle("Text App")
        self.setWindowIcon(QIcon(os.path.join(os.path.split(__file__)[0], "images", "4.ico")))
        self.resize(1200, 550)
        self.setAcceptDrops(True)
        self.initUI()
        self.fileopened = {} #index:file_path
        self.file_asterisk = False
        self.filesaved = {} #index:if_saved

### method to initialize the widgets
    def initUI(self):
        self.window = QWidget()

        self.menu()
        self.status()

        hbox = QHBoxLayout()
        self.main_layout = QSplitter(Qt.Horizontal)
        
        self.main_layout.setAcceptDrops(True)
        self.main_layout.addWidget(self.toolbar())

        self.tabs = QTabWidget()
        self.tabs.mouseDoubleClickEvent = lambda a0: self.addNewTab("untitled")
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_window)
        self.tabs.currentChanged.connect(self.get_row_column)
        self.main_layout.addWidget(self.tabs)
        self.main_layout.setSizes([50, 300])
        self.main_layout.setMidLineWidth(0)
        hbox.addWidget(self.main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_file)
        self.timer.start(1000)

        self.window.setLayout(hbox)
        self.initStyle()
        self.setCentralWidget(self.window)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.exists(path):
                self.file("o", [1, path])

##  method to return file type
    @staticmethod
    def get_file_type(name):
        lan = ""
        name = name.lower()
        # put different icons for different file types
        if name.endswith(".py"):
            lan = "python"
        elif name.endswith(".c"):
            lan = "c"
        elif name.endswith(".conf") or name.endswith(".cfg") or name.endswith(".config") or name.endswith(".ini"):
            lan = "config"
        elif name.endswith(".cpp"):
            lan = "cpp"
        elif name.endswith(".cs"):
            lan = "csharp"
        elif name.endswith(".go"):
            lan = "go"
        elif name.endswith(".html"):
            lan = "html"
        elif name.endswith(".jade"):
            lan = "jade"
        elif name.endswith(".java"):
            lan = "java"
        elif name.endswith(".js"):
            lan = "javascript"
        elif name.endswith(".json"):
            lan = "json"
        elif name.endswith(".less"):
            lan = "less"
        elif name.endswith(".markdown") or name.endswith(".md"):
            lan = "markdown"
        elif name.endswith(".php"):
            lan = "php"
        elif name.endswith(".ps1"):
            lan = "powershell"
        elif name.endswith(".jsx"):
            lan = "react"
        elif name.endswith(".rb"):
            lan = "ruby"
        elif name.endswith(".sass"):
            lan = "sass"
        elif name.endswith(".sh"):
            lan = "shell"
        elif name.endswith(".sql"):
            lan = "sql"
        elif name.endswith(".ts"):
            lan = "typescript"
        elif name.endswith(".vue"):
            lan = "vue"
        elif name.endswith(".xml"):
            lan = "xml"
        elif name.endswith(".yaml"):
            lan = "yaml"
        else:
            lan = "default"
        return lan

#### method to add tabs
    def addNewTab(self, name, data="", fp=""):
        def changesave():
            self.filesaved[self.tabs.currentIndex()] = False
            self.file_asterisk = True
            self.asterisk()
        widget = QWidget()
        vbox2 = QVBoxLayout(widget)
        
        # initialize text editor class and change properties if it is not an image
        if data == "image":
            image_lbl = QLabel(widget)
            img = QPixmap(fp)
            image_lbl.setAlignment(Qt.AlignCenter)
            image_lbl.setStyleSheet("background-color: black")
            transform =  QTransform().rotate(90)
            if img.height() > 500 or img.width() > 500:
                image_lbl.setPixmap(img.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            elif img.height() > img.width():
                image_lbl.setPixmap(img.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                image_lbl.setPixmap(img)
            self.tabs.addTab(widget, name)
            self.tabs.setCurrentIndex(self.tabs.count() - 1)
            self.tabs.currentWidget().setStyleSheet("color:black")
            self.setWindowTitle(f"{name} - {os.path.split(self.folder)[1]} - Text App") if self.folder != "" else  self.setWindowTitle(f"{name} - Text App")
            vbox2.addWidget(image_lbl)
        else:
            tab = TextEditor(widget)
            if name.endswith('.html'):
                data = html.unescape(data)
            tab.setText(data)
            tab.textChanged.connect(changesave)
            tab.setAcceptDrops(True)
            lan = self.get_file_type(name)
            icon = QPixmap(os.path.join(os.path.split(__file__)[0], "images", f"{lan}.ico"))
            self.tabs.addTab(widget, QIcon(icon), name)
            self.tabs.setCurrentIndex(self.tabs.count() - 1)
            vbox2.addWidget(tab)
            self.filesaved[self.tabs.currentIndex()] = True
            tab.cursorPositionChanged.connect(self.get_row_column)

        #refresh statusbar and menubar
        self.status()
        self.menu()

##  method to add and remove asterisk
    def asterisk(self):
        ## add asterisk if file is not saved and remove it if saved
        if self.file_asterisk and not self.filesaved[self.tabs.currentIndex()]:
            index = self.tabs.currentIndex()
            if not self.tabs.tabText(index).startswith("*"):
                if index in self.fileopened:
                    self.tabs.setTabText(index, f"*{os.path.split(self.fileopened[self.tabs.currentIndex()])[1]}")
                else:
                    self.tabs.setTabText(index, "*untitled")
        else:
            self.tabs.setTabText(self.tabs.currentIndex(), f"{os.path.split(self.fileopened[self.tabs.currentIndex()])[1]}")
            self.setWindowTitle(f"{os.path.split(self.fileopened[self.tabs.currentIndex()])[1]} - {os.path.split(self.folder)[1]} - Text App") if self.folder != "" else  self.setWindowTitle(f"{os.path.split(self.fileopened[self.tabs.currentIndex()])[1]} - Text App")

#### method to get text editor of the current tab 
    def current_text_edit(self):
        return self.tabs.currentWidget().findChild(QTextEdit)

#### method to close window tab
    def close_window(self, tab=""):
        def close():
            if self.tabs.tabText(self.tabs.currentIndex()) in self.fileopened.values():
                self.fileopened.pop(self.tabs.currentIndex())
                self.filesaved.pop(self.tabs.currentIndex())
            if tab == "":
                self.tabs.removeTab(self.tabs.currentIndex())
            else:
                self.tabs.removeTab(tab)
            self.menu()
            self.status()

        if self.filesaved[self.tabs.currentIndex()]:
            close()
            self.setWindowTitle(f"{self.tabs.tabText(self.tabs.currentIndex())} - {self.folder} - Text App") if self.folder != "" else self.setWindowTitle(f"{self.tabs.tabText(self.tabs.currentIndex())} - Text App")
            if self.tabs.count() == 0: self.setWindowTitle("Text App")
        else:
            reply = QMessageBox.warning(self, "Unsaved Tab", 
                                "Do you want to close the unsaved tab", 
                                QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.Yes:
                close()

#### method to add a toolbar
    def toolbar(self):
        self.scroller = QScrollArea()
        file_view = QTreeView()

        # Set up the model
        model = QFileSystemModel()
        model.setRootPath(QDir.rootPath())
        file_view.setModel(model)

        # Set root to the current folder (if available)
        if self.folder != "":
            file_view.setRootIndex(model.index(self.folder))
        else:
            file_view.setRootIndex(model.index(QDir.homePath()))    

        # Enable dragging
        file_view.setDragEnabled(True)
        file_view.setAcceptDrops(False)
        file_view.setDropIndicatorShown(True)
        file_view.setSelectionMode(file_view.SingleSelection)

        # On double click, open the file
        file_view.doubleClicked.connect(lambda index: self.file("o", [1, model.filePath(index)]))

        self.scroller.setWidgetResizable(True)
        self.scroller.setWidget(file_view)
        return self.scroller

#### method to sort folders
    def get_folder(self):
        self.folder = QFileDialog.getExistingDirectory(caption="Open Any Folder")
        self.recent_files.append(f"{self.folder}")
        self.add_recent()
        self.scroller.close()
        self.initUI()

#### method to create menu bar
    def menu(self):
        menubar = QMenuBar()
        self.setMenuBar(menubar)

        # File Actions
        file = menubar.addMenu("File")
        file_commands = (["New", "Ctrl+N"], ["Save", "Ctrl+S"], ["Open", "Ctrl+O"], ["Open Folder", "Ctrl+Shift+F"], ["Save As", "Ctrl+Shift+S"],
                         ["New Window", "Ctrl+Shift+N"], ["Open External Command Prompt", "Ctrl+Shift+C"], ["Close Tab", "Ctrl+W"], ["Quit", "Ctrl+Q"])
        for i in file_commands:
            action = QAction(i[0], self)
            action.setShortcut(i[1])
            file.addAction(action)

            # Disable some menu commands if no tabs are open
            if not hasattr(self, "tabs"):
                if action.text() == "Save" or action.text() == "Close Tab" or action.text() == "Save as":
                    action.setEnabled(False)
            else:
                if self.tabs.count() == 0:
                    if action.text() == "Save" or action.text() == "Close Tab" or action.text() == "Save as":
                        action.setEnabled(False)
            if i == ["Close Tab", "Ctrl+W"]:
                file.addSeparator()
                recent = file.addMenu("Recent Files")
                self.recent_filepath = os.path.join(self.save_directory, "recent.lst")
                if os.path.exists(self.recent_filepath):
                    with open(self.recent_filepath, "r") as f:
                        for i in f.read().split(";"):
                            if i != "":
                                recent.addAction(i)
                                self.recent_files.append(i)
                else:
                    open(self.recent_filepath, "w").close()
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
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        # if tab is no tab currently open, the statusbar will  be empty
        if hasattr(self, 'tabs'):
            if self.tabs.count() > 0:
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
            self.setWindowTitle(f"{self.tabs.tabText(self.tabs.currentIndex())} - {os.path.split(self.folder)[1]} - Text App") if self.folder != "" else  self.setWindowTitle(f"{self.tabs.tabText(self.tabs.currentIndex())} - Text App")

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
        command = command.text()
        match command:
            case "New":
                self.addNewTab("untitled")
            case "Save":
                self.file("s")
            case "Open":
                self.file("o")
            case "Save As":
                self.file("s", ["saveas", ''])
            case "New Window":
                new_win = TextApp()
                new_win.setGeometry(self.x()-10, self.y()+50, self.width(), self.height())
                new_win.show()
                self.child_windows.append(new_win)
            case "Open Folder":
                self.get_folder()
                self.tabs.clear()
            case "Close Tab":
                self.close_window()
            case "Clear":
                with open(self.recent_filepath, "w") as f:
                    f.write("")
                self.recent_files.clear()
                self.menu()
            case "Open External Command Prompt":
                os.system("start")
            case "Quit":
                check = QMessageBox(QMessageBox.Question, "Exit", "Do you really want to exit", QMessageBox.Yes|QMessageBox.No)
                check.buttonClicked.connect(lambda e: self.close() if e.text() == "&Yes" else e.text())
                check.exec_()
            case "Copy":
                if self.tabs.count() != 0:
                    self.clip.setText(self.current_text_edit().textCursor().selectedText())
            case "Paste":
                if self.tabs.count() != 0:
                    cursor = self.current_text_edit().textCursor()
                    cursor.insertText(self.clip.text())
            case "Find/Replace":
                if self.tabs.count() != 0:
                    dlg = FindReplaceDialog(self)
                    dlg.show()
            case "Documentation":
                QMessageBox.about(self, "Documentation",
                                  """
                                  Open the menu for commands and you can use shortcuts
                                  """)
            case "About":
                QMessageBox.about(self, "About", "Created in Nigeria by Calvin")
            case _:
                self.file("o", [1, command])

#### method to add recent file
    def add_recent(self):
        files = set()
        try:
            path = self.recent_filepath
            with open(path, "r") as k:
                for j in k.read().split(";"):
                    self.recent_files.append(f"{j}")
            with open(path, "w") as h:
                for j in self.recent_files:
                    files.add(j)
                h.write(";".join(files))
            self.menu()
        except FileNotFoundError:
            open(path, "w").close()

#### method to open and save file
    def file(self, file_handling, mode=[0, ""]):
        files = """
            All Files(* *.);;
            Text Files (*.txt);;
            Python Files (*.py *.pyw *.pyc);;
            C Files (*.c);;
            Config Files (*.conf *.cfg *.config *.ini);;
            C++ Files (*.cpp);;
            C# Files (*.cs);;
            CSS Files (*.css);;
            GO Files (*.go);;
            HTML Files (*.html);;
            Jade Files (*.jade);;
            Java Files (*.java);;
            JSON Files (*.json);;
            LESS Files (*.less);;
            Markdown Files (*.md *.markdown);;
            PHP Files (*.php);;
            Powershell Files (*.ps1);;
            React Files (*.jsx);;
            Ruby Files (*.rb);;
            Sass Files (*.sass);;
            Shell Files (*.sh);;
            SQL Files (*.sql);;
            TypeScript Files (*.ts);;
            Vue Files (*.vue);;
            XML Files (*.xml);;
            Yaml Files (*.yaml)
        """
        images = [".png", ".jpg", ".ico", ".webp", ".jpeg"]
        if file_handling == "o":
            if mode[0] == 1:
                if mode[1] not in self.fileopened.values():
                    if os.path.exists(mode[1]):
                        if os.path.isdir(mode[1]):
                            self.folder = mode[1]
                            self.scroller.close()
                            self.initUI()
                        else:
                            if mode[1][mode[1].rindex("."):] in images:
                                self.addNewTab(name= os.path.split(mode[1])[1], data="image", fp=mode[1])
                                self.fileopened[self.tabs.currentIndex()] = mode[1]
                                self.filesaved[self.tabs.currentIndex()] = True
                            else:
                                try:
                                    with open(mode[1], "r") as f:
                                        # get filename name
                                        filename_and_path = os.path.split(mode[1])
                                        filename = filename_and_path[1]
                                        # open a new tab and select that tab
                                        self.addNewTab(filename, f.read())
                                        self.tabs.setCurrentIndex(self.tabs.count()-1)
                                        self.fileopened[self.tabs.currentIndex()] = mode[1]
                                        self.filesaved[self.tabs.currentIndex()] = True
                                except UnicodeDecodeError:
                                    QMessageBox.warning(self, "Unable to open", "Cannot open file type")
                    else:
                        QMessageBox.warning(self, "Warning", "File is not found")
                else:
                    for count, i in enumerate(self.fileopened.keys()):
                        if self.fileopened[count] == mode[1]:
                            self.tabs.setCurrentIndex(i)
            else:
                while True:
                    current = ""
                    try:current = QDir.homePath() if self.tabs.count() == 0 else os.path.split(self.fileopened[self.tabs.currentIndex()])[0]
                    except:pass
                    if self.folder != "": current = self.folder
                    dialog = QFileDialog()
                    dialog.setMinimumSize(300, 200)
                    file = dialog.getOpenFileName(self, "Open File", current, 
                                                    files
                                                    )
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
                                self.recent_files.append(f"{file[0].replace("\\", "/")}")
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
                        images = [".png", ".jpg", ".webp", ".jpeg", ".ico"]
                        if file[0][file[0].rindex("."):] in images:
                            self.addNewTab(name=os.path.split(file[0])[1], data="image", fp=file[0])
                            self.fileopened[self.tabs.currentIndex()] = mode[1]
                            self.filesaved[self.tabs.currentIndex()] = True
                            self.recent_files.append(f"{file[0].replace("\\", "/")}")
                            self.add_recent()
                            break
        elif file_handling == "s":
            if self.tabs.count() > 0 and self.tabs.currentIndex() not in self.fileopened or mode[0] == "saveas":
                dialog = QFileDialog()
                dialog.setMinimumSize(300, 200)
                file = dialog.getSaveFileName(self, "Save File", os.path.split(__file__)[0], 
                                                files
                                                )
                try:
                    with open(file[0], "w") as f:
                        filename_and_path = os.path.split(file[0])
                        # get filename
                        self.filename = filename_and_path[1]
                        # create a file and write the content of the tab in it change the tab's text
                        f.write(self.current_text_edit().toPlainText())
                        self.tabs.setTabText(self.tabs.currentIndex(), self.filename)
                        lan = self.get_file_type(self.filename)
                        icon = QPixmap(os.path.join(os.path.split(__file__)[0]+"/images", f"{lan}.ico"))
                        self.tabs.setTabIcon(self.tabs.currentIndex(), 
                                             QIcon(icon)
                                            )
                        self.setWindowTitle(f"{self.filename} - {os.path.split(self.folder)[1]} - Text App") if self.folder != "" else  self.setWindowTitle(f"{self.filename} - Text App")

                        self.fileopened[self.tabs.currentIndex()] = file[0]
                        self.filesaved[self.tabs.currentIndex()] = True
                        self.recent_files.append(f"{file[0].replace("\\", "/")}")
                        self.add_recent()
                        self.menu()
                except FileNotFoundError:
                    QMessageBox(QMessageBox.Critical, "No File", "No file was selected").exec_()
                except Exception:
                    pass
            else:
                try:
                    with open(self.fileopened[self.tabs.currentIndex()], "w") as f:
                        f.write(self.current_text_edit().toPlainText())
                        self.filesaved[self.tabs.currentIndex()] = True
                        self.file_asterisk = False
                        self.asterisk()
                except Exception:
                    pass
    def update_file(self):
        images = [".png", ".jpg", ".webp", ".jpeg", ".ico"]
        for i, j in self.fileopened.items():
            if not os.path.isdir(j):
                if j[j.rindex("."):len(j)] not in images:
                    try:
                        with open(j, "r") as f:
                            disk_content = f.read()
                        editor = self.tabs.widget(i).findChild(QTextEdit)
                        current_content = editor.toPlainText()
                        if disk_content != current_content and self.filesaved[i]:
                            editor.blockSignals(True) # to prevent textChanged event
                            editor.setPlainText(disk_content)
                            editor.blockSignals(False)
                            self.asterisk()
                    except FileNotFoundError:
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
