from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel, QHBoxLayout, QStatusBar, \
    QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QButtonGroup, QFileDialog, \
    QLineEdit, QInputDialog
from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
import sys
import json
import os
from CanvasAPI import download_canvas

VERSION = 1.1

try:
    with open("configuration.json", "r") as f:
        data = json.load(f)  # important concept!! This doesn't reflect the outer data change once it's read
        if "sync_on" not in data:  # for ver 1.0 backward compatibility
            data["sync_on"] = True
        if "canvas_struct" not in data:
            data["canvas_struct"] = True
except FileNotFoundError:
    data = {
        "folder_path_short": "None",
        "folder_path_abs": "None",
        "secret_token": "None",
        "sync_on": True,
        "canvas_struct": True,
        "class_code": "0",
    }
# print(data)


class Window(QMainWindow):
    def __init__(self, parent=None):
        # Init and prepare
        super().__init__(parent)
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self.generalLayout = QVBoxLayout()
        self.generalLayout.setAlignment(Qt.AlignTop)
        self._centralWidget.setLayout(self.generalLayout)
        
        # Basic configuration
        self.setWindowTitle(f"Canvas Downloader v{VERSION}")
        self.setFixedSize(500, 600)
        
        # Initialize widgets
        self._createConfigForm()
        self._createStatus()
        self._createConnection()
        self._configureThread()
        self._outputWelcomeMsg()
        
    def _createConfigForm(self):
        # Add widgets ------------------------------------------------------------------------------
        self.btn_set_secret = QPushButton("Set")
        self.secret_token_str = QLabel(f"Token Status: {'Exist' if data['secret_token'] != 'None' else 'None'}")
        self.btn_select_dest = QPushButton("Change")
        self.destination_folder = QLabel(f"Target Folder: {data['folder_path_short']}")
        self.btn_save_run = QPushButton("Save + Run")
        
        # Set object name to save path for later access
        self.destination_folder.setObjectName(data['folder_path_abs'])
        self.secret_token_str.setObjectName(data['secret_token'])
        
        # Toggle Buttons ------------------------------------------------------------------------------
        self.sync_group = QButtonGroup()
        self.sync_mode = QRadioButton("On")
        sync_mode_off = QRadioButton("Off")
        self.sync_group.addButton(self.sync_mode, 1)
        self.sync_group.addButton(sync_mode_off, 2)
        
        self.canvas_struct_group = QButtonGroup()
        self.canvas_struct_on = QRadioButton("On")
        canvas_struct_off = QRadioButton("Off")
        self.canvas_struct_group.addButton(self.canvas_struct_on, 1)
        self.canvas_struct_group.addButton(canvas_struct_off, 2)
        
        self.class_code_input = QLineEdit()
        self.class_code_input.setValidator(QIntValidator())
        self.class_code_input.setText(data["class_code"])
        # self.class_code_input.setMinimumWidth(70)
        
        self.sync_mode.setChecked(True) if data["sync_on"] else sync_mode_off.setChecked(True)
        self.canvas_struct_on.setChecked(True) if data["canvas_struct"] else canvas_struct_off.setChecked(True)
        
        # Add to layout ------------------------------------------------------------------------------
        self.formGroupBox = QGroupBox()
        self.formGroupBoxLayout = QVBoxLayout()
        
        self.helper_add_hs([self.btn_set_secret, self.secret_token_str], self.formGroupBoxLayout)
        self.helper_add_hs([self.btn_select_dest, self.destination_folder], self.formGroupBoxLayout)
        self.helper_add_hs([QLabel("Sync Mode:"), self.sync_mode, sync_mode_off], self.formGroupBoxLayout)
        self.helper_add_hs([QLabel("Canvas Structure:"), self.canvas_struct_on, canvas_struct_off], self.formGroupBoxLayout)
        self.helper_add_hs([QLabel("Class Code:"), self.class_code_input], self.formGroupBoxLayout)
        self.helper_add_hs([self.btn_save_run, QLabel("Click here to save setting and run")], self.formGroupBoxLayout)
        
        self.formGroupBox.setLayout(self.formGroupBoxLayout)
        self.generalLayout.addWidget(self.formGroupBox)
    
    def _configureThread(self):
        self.thread = CanvasDownloadThread(self)
        self.thread.thread_output.connect(self.thread_print)  # Output
        self.thread.is_running.connect(self.canvas_running)
        
    def _createStatus(self):
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        self.generalLayout.addWidget(self.output)
    
    def _createConnection(self):
        # self.sync_mode.toggled.connect(lambda x: [btn.setDisabled(not x) for btn in self.method_group.buttons()])
        self.btn_set_secret.clicked.connect(self.input_secret_token)
        self.btn_select_dest.clicked.connect(self.chooseFile)
        self.btn_save_run.clicked.connect(self.runGrabCanvas)
        # Note: Do not need to create connection for the button group since they're connected!

    def _outputWelcomeMsg(self):
        self.output.append("Thank you for trying out this mini program 💜")
        self.output.append("Prepare to download from canvas!")
        self.output.append(74 * "-")
        self.status.showMessage("You haven't done anything yet ~ currently idle status")
        
    def thread_print(self, print_this):  # DONT declare these as SLOTS!
        # Get the print text from thread, the reason we do it here because it's BETTER to update GUI in the main thread
        self.output.append(print_this)
    
    def canvas_running(self, is_running):
        if not is_running:  # If process finished
            self.output.append(34 * "-" + "Done" + 34 * "-")
            self.status.showMessage("Finished, hope you have a great day!")
        else:
            self.status.showMessage("I'm fetching resources... you can get yourself a cookie")
    
    @pyqtSlot()
    def chooseFile(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        shorter_path = abs_path = file_dialog.getExistingDirectory(self, "Choose Folder")
        
        if abs_path:  # if there's a input
            while len(shorter_path) >= 35:  # Shorten file name
                shorter_path = "..." + shorter_path.split("/", 1)[1]
            
            self.destination_folder.setText(f"Target Folder: {shorter_path}")
            self.destination_folder.setObjectName(abs_path)
            self.destination_folder.repaint()
            self.output.append(f"Changed save location to: {abs_path}")
            self.output.repaint()
    
    @pyqtSlot()
    def input_secret_token(self):
        token, done = QInputDialog().getText(self, 'Token Setter', 'Enter your token: ', QLineEdit.Normal, self.secret_token_str.objectName())
        if done:
            self.secret_token_str.setText("Token Status: Exist")
            self.secret_token_str.setObjectName(token)
            self.output.append("Token updated! I'll automatically save for future use")
            self.saveSetting()
            # self.output.append(f"Token: {token}")
    
    def saveSetting(self):
        new_data = {
            "folder_path_short": self.destination_folder.text().split(": ", 1)[1],
            "folder_path_abs": self.destination_folder.objectName(),
            "secret_token": self.secret_token_str.objectName(),
            "sync_on": self.sync_mode.isChecked(),
            "canvas_struct": self.canvas_struct_on.isChecked(),
            "class_code": self.class_code_input.text(),
        }
        # print(new_data)
        
        with open("configuration.json", "w") as f:
            json.dump(new_data, f)
        
        self.output.append("Configuration saved!")
    
    @pyqtSlot()
    def runGrabCanvas(self):  # do your algorithm here
        # Check before running
        if not os.path.isdir(self.destination_folder.objectName()):
            self.output.append("Your folder path is empty OR it is not a directory!")
            return
        elif self.secret_token_str.objectName() == "None":
            self.output.append("Your token is empty!")
            return
        
        # Start your process here (Multi threading)
        self.thread.start()
    
    def closeEvent(self, QCloseEvent):  # Save while closing
        self.saveSetting()
        QCloseEvent.accept()
    
    @staticmethod
    def helper_add_hs(widgets, to_layout):  # helper function to add horizontal layout on top
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignLeft)
        widgets[0].setFixedWidth(120)
        for widget in widgets:
            h_layout.addWidget(widget)
        to_layout.addLayout(h_layout)


class CanvasDownloadThread(QThread):
    thread_output = pyqtSignal(str)
    is_running = pyqtSignal(bool)
    
    def __init__(self, gui_instance):
        super(CanvasDownloadThread, self).__init__()
        self.gui_instance = gui_instance
    
    def run(self):
        """Long running task, multithreading download canvas function"""
        self.is_running.emit(True)
        download_canvas(self.gui_instance.secret_token_str.objectName(),
                        self.gui_instance.class_code_input.text(),
                        self.gui_instance.destination_folder.objectName(),
                        self.thread_output.emit,
                        self.gui_instance.sync_mode.isChecked(),
                        self.gui_instance.canvas_struct_on.isChecked())
        self.is_running.emit(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = Window()
    view.show()
    sys.exit(app.exec())
