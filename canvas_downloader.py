from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel, QHBoxLayout, QStatusBar, \
    QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QButtonGroup, QFileDialog, \
    QLineEdit, QInputDialog, QLayout, QBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
import sys
import os
from utils import get_application_setting, ConfigKey, print_middle, check_setting
from canvas_api import download_canvas

# Global value
APP_VERSION = 1.2
app_setting = get_application_setting(initialise=True)

class Window(QMainWindow):
    def __init__(self, parent=None):
        # Initialise layouts and widgets
        super().__init__(parent)
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self.generalLayout = QVBoxLayout()
        self.generalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._centralWidget.setLayout(self.generalLayout)
        
        # Basic configuration
        self.setWindowTitle(f"Canvas下载器 v{APP_VERSION}")
        self.setFixedSize(500, 600)
        
        # Initialize widgets
        self._createConfigForm()
        self._createStatus()
        self._createConnection()
        self._configureThread()
        self._outputWelcomeMsg()
    
    def _createConfigForm(self):
        # Add widgets ------------------------------------------------------------------------------
        self.btn_set_secret = QPushButton("设置")
        self.secret_token_str = QLabel(
            f"Canvas令牌状态: {'存在' if app_setting.value(ConfigKey.SECRET_TOKEN) != '无' else '无'}")
        self.btn_select_dest = QPushButton("更改")
        self.destination_folder = QLabel(
            f"目标路径: {self.get_trimmed_path(app_setting.value(ConfigKey.FOLDER_PATH_ABS))}")
        self.btn_save_run = QPushButton("保存并运行")
        
        # Toggle Buttons ------------------------------------------------------------------------------
        self.sync_group = QButtonGroup()
        self.sync_mode = QRadioButton("开启")
        sync_mode_off = QRadioButton("关闭")
        self.sync_group.addButton(self.sync_mode, 1)
        self.sync_group.addButton(sync_mode_off, 2)
        
        self.canvas_struct_group = QButtonGroup()
        self.canvas_struct_on = QRadioButton("开启")
        canvas_struct_off = QRadioButton("关闭")
        self.canvas_struct_group.addButton(self.canvas_struct_on, 1)
        self.canvas_struct_group.addButton(canvas_struct_off, 2)
        
        self.class_code_input = QLineEdit()
        self.class_code_input.setValidator(QIntValidator())
        self.class_code_input.setText(app_setting.value(ConfigKey.CLASS_CODE))
        # self.class_code_input.setMinimumWidth(70)
        
        self.sync_mode.setChecked(True) if app_setting.value(ConfigKey.SYNC_ON) else sync_mode_off.setChecked(True)
        self.canvas_struct_on.setChecked(True) if app_setting.value(ConfigKey.CANVAS_STRUCT) else canvas_struct_off.setChecked(
            True)
        
        # Add to layout ------------------------------------------------------------------------------
        self.formGroupBox = QGroupBox()
        self.formGroupBoxLayout = QVBoxLayout()
        
        self.helper_add_hs([self.btn_set_secret, self.secret_token_str], self.formGroupBoxLayout)
        self.helper_add_hs([self.btn_select_dest, self.destination_folder], self.formGroupBoxLayout)
        self.helper_add_hs([QLabel("同步模式:"), self.sync_mode, sync_mode_off], self.formGroupBoxLayout)
        self.helper_add_hs([QLabel("Canvas文件结构:"), self.canvas_struct_on, canvas_struct_off],
                           self.formGroupBoxLayout)
        self.helper_add_hs([QLabel("课程号码:"), self.class_code_input], self.formGroupBoxLayout)
        self.helper_add_hs([self.btn_save_run, QLabel("保持当前设置并运行程序")], self.formGroupBoxLayout)
        
        self.formGroupBox.setLayout(self.formGroupBoxLayout)
        self.generalLayout.addWidget(self.formGroupBox)
    
    def _configureThread(self):
        self.thread = CanvasDownloadThread(self)
        self.thread.thread_output.connect(self.thread_print)
        self.thread.is_running.connect(self.update_display_canvas_running)
    
    def _createStatus(self):
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        self.generalLayout.addWidget(self.output)
    
    def _createConnection(self):
        """
        Define button connections with corresponding slot
        """
        # self.sync_mode.toggled.connect(lambda x: [btn.setDisabled(not x) for btn in self.method_group.buttons()])
        self.btn_set_secret.clicked.connect(self.enterCanvasSecretToken)
        self.btn_select_dest.clicked.connect(self.chooseSaveDstFile)
        self.btn_save_run.clicked.connect(self.runGrabCanvas)
        # Note: Do not need to create connection for the button group since they're connected!
    
    def _outputWelcomeMsg(self):
        """
        Starting message to print to user
        """
        self.output.append(f"感谢你使用Canvas下载器v{APP_VERSION} 💜")
        self.output.append("准备就绪！")
        print_middle("", self.output.append)
        self.status.showMessage("下载器正在等你发布指令喔～")
    
    def thread_print(self, print_this: str):
        """
        Get string output from download thread and print it to user
        the reason we do it this way is that it's BETTER to update the GUI in the main thread

        Args:
            print_this: content to print to user
        """
        self.output.append(print_this)
    
    def update_display_canvas_running(self, is_running: bool):
        """
        Output information to user based on the status of downloading thread

        Args:
            is_running: exist running downloading task
        """
        if is_running:
            self.status.showMessage("下载器正在努力的获得资源。。。")
        else:
            print_middle("完成✅", self.output.append)
            self.status.showMessage("下载器正在休息～")
    
    @pyqtSlot()
    def chooseSaveDstFile(self):
        """
        Select a folder as the download destination
        """
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        abs_path = file_dialog.getExistingDirectory(self, "选择保存的文件夹")
        
        if abs_path:  # if there's a valid input
            shorter_path = self.get_trimmed_path(abs_path)
            
            self.destination_folder.setText(f"目标路径: {shorter_path}")
            self.saveSetting(update_config_code={ConfigKey.FOLDER_PATH_ABS: abs_path})
            self.destination_folder.repaint()
            self.output.append(f"目标路径更改为: {abs_path}")
            self.output.repaint()
    
    @pyqtSlot()
    def enterCanvasSecretToken(self):
        """
        Open a dialog to let the user set their canvas token
        """
        token, done = QInputDialog().getText(self, '设置Canvas令牌', '请输入你的Canvas令牌: ',
                                             QLineEdit.EchoMode.Normal, app_setting.value(ConfigKey.SECRET_TOKEN))
        
        if done:
            self.secret_token_str.setText("Canvas令牌状态: 存在")
            self.saveSetting(update_config_code={ConfigKey.SECRET_TOKEN: token})
            self.output.append("已更新Canvas令牌，正在保存设置。。。")
            self.saveSetting()
            # self.output.append(f"Token: {token}")
        else:
            self.output.append("取消设置Canvas令牌")
    
    def saveSetting(self, update_config_code: {} = None):
        """
        Crawl and save new application settings
        """
        # Default empty update code config
        if update_config_code is None:
            update_config_code = {}
        
        # Crawl update value from UI
        update_config_ui = {
            ConfigKey.SYNC_ON: self.sync_mode.isChecked(),
            ConfigKey.CANVAS_STRUCT: self.canvas_struct_on.isChecked(),
            ConfigKey.CLASS_CODE: self.class_code_input.text(),
        }
        
        # Save value from UI
        for new_config_key, new_config_val in update_config_ui.items():
            app_setting.setValue(new_config_key, new_config_val)
        
        # Save value from code
        for new_config_key, new_config_val in update_config_code.items():
            app_setting.setValue(new_config_key, new_config_val)
        
        self.output.append("已保存新的设置!")
    
    @pyqtSlot()
    def runGrabCanvas(self):
        """
        Check required arguments and run canvas download thread
        """
        self.saveSetting()
        # Pre check
        valid_setting, err_reason = check_setting()
        if not valid_setting:
            self.output.append(err_reason)
            return
        
        # Trigger download logic in another thread
        self.thread.start()
    
    def closeEvent(self, QCloseEvent):
        """
        Save setting when we exit the application

        Args:
            QCloseEvent: CloseEvent argument provided by qt
        """
        self.saveSetting()
        QCloseEvent.accept()
    
    @staticmethod
    def helper_add_hs(widgets: [QWidget], to_layout: QVBoxLayout):
        """
        helper function to add a list of left aligned widgets as a horizontal layout to a vertical layout

        Args:
            widgets: list of QWidget to turn into horizontal layout
            to_layout: the vertical layout to add to
        """
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        widgets[0].setFixedWidth(120)
        for widget in widgets:
            h_layout.addWidget(widget)
        to_layout.addLayout(h_layout)
    
    @staticmethod
    def get_trimmed_path(original_path: str, len_threshold: int = 35) -> str:
        """
        Shorten path string for trimmed display
        
        Args:
            original_path: absolute path string
            len_threshold: trim to threshold

        Returns:
            A trimmed path
        """
        while len(original_path) >= len_threshold:
            if len(original_path.split("/", 1)) == 1:
                break
            original_path = "...." + original_path.split("/", 1)[1]
        return original_path


class CanvasDownloadThread(QThread):
    thread_output = pyqtSignal(str)
    is_running = pyqtSignal(bool)
    
    def __init__(self, gui_instance):
        super(CanvasDownloadThread, self).__init__()
        self.gui_instance = gui_instance
    
    def run(self):
        """
        Run download task in another thread
        """
        self.is_running.emit(True)
        download_canvas(self.thread_output.emit)
        self.is_running.emit(False)


if __name__ == '__main__':
    # Application entry
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('resources/canvas.ico')) # You can comment this out if you don't have the icon
    view = Window()
    view.show()
    sys.exit(app.exec())
