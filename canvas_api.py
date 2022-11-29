from canvasapi import Canvas, exceptions
from typing import Callable
import os


def download_canvas(secret_token: str, course_num: int, save_to_path: str,
                    print_output: Callable[[str], None], sync_on: bool, canvas_struct: bool) -> None:
    """
    Download files from canvas
    
    Args:
        secret_token: token to access canvas api
        course_num: course number to download from
        save_to_path: which folder to save to
        print_output: output function (eg: terminal or qt output)
        sync_on:
        canvas_struct:
    """
    try:
        canvas = Canvas("https://oc.sjtu.edu.cn/", secret_token)  # Init
        course = canvas.get_course(course_num)
    except exceptions.InvalidAccessToken:
        print_output("下载失败，请检查你的口令牌")
        return
    except exceptions.ResourceDoesNotExist:
        print_output("FAILED. Check your course number!")
        return
    except:
        print_output("FAILED. Unknown error occur while trying to connect with canvas!")
        return
    
    # variables to get all the files in the current save path first for a LOOKUP table
    current_files = set()  # print this to debug
    new_files_idx = 0
    for dir_path, dir_names, filenames in os.walk(save_to_path):
        current_files.update(filenames)
    
    for folder in course.get_folders():  # Get all folders in a course, it contains all sub-folders as well !
        # Extract the top folder path
        folder_top = "" if str(folder) == 'course files' else str(folder).split('/', 1)[1]
        print_output(f"Currently at: {folder_top if folder_top else 'Canvas Home'}")
        folder_top = "" if not canvas_struct else folder_top  # Check download directory structure

        # Download files
        for file in folder.get_files():
            if not sync_on or str(file) not in current_files:  # Download checking condition
                try:
                    print_output(f"Downloading file {new_files_idx + 1} inside {folder_top if folder_top else 'Canvas Home'}... -> {file}")
                    # Create folder to replicate canvas structure
                    os.makedirs(os.path.join(save_to_path, folder_top), exist_ok=True)
                    file.download(os.path.join(save_to_path, folder_top, str(file)))
                    new_files_idx += 1  # only increment after download because it might have error during download
                except exceptions.ResourceDoesNotExist:
                    print_output(f"Download error: You might not have permission to access this file.")
    
    # Status report
    print_output(f"Finished, there's {new_files_idx} newly added files.")


if __name__ == '__main__':
    # FOR DEBUGGING
    API_KEY = os.getenv("SJTU_CANVAS_KEY")
    COURSE_NUMBER = 28295
    SAVE_FOLDER_LOC = "/Users/lunafreya/Downloads/untitled"
    download_canvas(API_KEY, COURSE_NUMBER, SAVE_FOLDER_LOC, print, True, True)
