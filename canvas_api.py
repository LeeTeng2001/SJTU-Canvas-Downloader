from canvasapi import Canvas, exceptions
from typing import Callable
import os
from pathlib import Path
from utils import get_application_setting, ConfigKey

app_setting = get_application_setting()

def download_canvas(print_output: Callable[[str], None]) -> None:
    """
    Download files from canvas
    
    Args:
        print_output: output function (eg: terminal or qt output)
    """
    canvas_struct = app_setting.value(ConfigKey.CANVAS_STRUCT)
    sync_on = app_setting.value(ConfigKey.SYNC_ON)
    download_to_folder = app_setting.value(ConfigKey.FOLDER_PATH_ABS)
    
    try:
        canvas = Canvas("https://oc.sjtu.edu.cn/", app_setting.value(ConfigKey.SECRET_TOKEN))
        course = canvas.get_course(app_setting.value(ConfigKey.CLASS_CODE))
    except exceptions.InvalidAccessToken:
        print_output("下载失败：请检查你的口令牌")
        return
    except ValueError:
        print_output("下载失败：请确保课程号码已经设置")
        return
    except exceptions.ResourceDoesNotExist:
        print_output("下载失败：课程号码不存在，请检查")
        return
    except exceptions.CanvasException:
        print_output("下载失败：Canvas状态异常")
        return
    except Exception:
        print_output("下载失败：遇到未知错误")
        return
    
    # variables to get all the files in the current save path first for a LOOKUP table
    current_files = set()  # print this to debug
    new_files_idx = 0
    for dir_path, dir_names, filenames in os.walk(download_to_folder):
        current_files.update(filenames)

    for folder in course.get_folders():  # Get all folders in a course, it contains all sub-folders as well !
        # Extract the top folder path
        folder_top = "" if str(folder) == 'course files' else str(folder).split('/', 1)[1]
        print_output(f"正在爬取: {folder_top if folder_top else 'Canvas Home'}")
        folder_top = "" if not canvas_struct else folder_top  # Check download directory structure

        # Download files
        for file in folder.get_files():
            if not sync_on or str(file) not in current_files:  # Download checking condition
                try:
                    print_output(f"位于{folder_top if folder_top else 'Canvas Home'}，正在下载文件：{file}")
                    
                    # Create folder to replicate canvas structure
                    Path(download_to_folder, folder_top).mkdir(parents=True, exist_ok=True)
                    file.download(Path(app_setting.value(ConfigKey.FOLDER_PATH_ABS), folder_top, str(file)).as_posix())
                    new_files_idx += 1  # only increment after download because it might have error during download
                except exceptions.ResourceDoesNotExist:
                    print_output(f"下载失败：资源不存在")
                except exceptions.Unauthorized:
                    print_output(f"下载失败：没有权限")
    
    # Status report
    print_output(f"下载结束，总共下载了{new_files_idx}个文件。")


if __name__ == '__main__':
    # FOR DEBUGGING
    API_KEY = os.getenv("SJTU_CANVAS_KEY")
    # COURSE_NUMBER = 28295
    # SAVE_FOLDER_LOC = "/Users/lunafreya/Downloads/untitled"
    # download_canvas(API_KEY, COURSE_NUMBER, SAVE_FOLDER_LOC, print, True, True)
