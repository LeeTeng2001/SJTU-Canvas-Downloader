from PyQt6.QtCore import QSettings
from typing import Callable
from pathlib import Path
from enum import Enum

class ConfigKey(str, Enum):
    FOLDER_PATH_ABS = "folder_path_abs"
    SECRET_TOKEN = "secret_token"
    SYNC_ON = "sync_on"
    CANVAS_STRUCT = "canvas_struct"
    CLASS_CODE = "class_code"

DEFAULT_CONFIG_VAL = {
    ConfigKey.FOLDER_PATH_ABS: "无",
    ConfigKey.SECRET_TOKEN: "无",
    ConfigKey.SYNC_ON: True,
    ConfigKey.CANVAS_STRUCT: True,
    ConfigKey.CLASS_CODE: "0",
}

def get_application_setting(initialise=False) -> QSettings:
    """
    Get the QSettings object to access application configuration

    Args:
        initialise: Initialise each missing setting key with a default value

    Returns:
        QSettings object
    """
    settings = QSettings("sjtu", "lunafreya-canvas-downloader")
    
    # Set default value for non-existence key
    if initialise:
        print(f"Config file location：{settings.fileName()}")
        for config_key, config_val in DEFAULT_CONFIG_VAL.items():
            if not settings.contains(config_key):
                settings.setValue(config_key, config_val)
    
    return settings

def check_setting() -> (bool, str):
    """
    Check validity of each setting
    
    Returns:
        (True, None) if passed
        (False, err_reason) if failed
    """
    setting = get_application_setting()
    if not Path(setting.value(ConfigKey.FOLDER_PATH_ABS)).is_dir():
        return False, "违法目标路径"
    if len(setting.value(ConfigKey.CLASS_CODE)) == 0:
        return False, "不能有空的课程号码"
    
    return True, None

def print_middle(content: str, print_to: Callable[[str], None], print_length: int = 72):
    remaining_length = print_length - len(content.encode('utf-8'))
    left_len = int(remaining_length / 2)
    right_len = remaining_length - left_len
    
    print_to(left_len * "-" + content + right_len * "-")
