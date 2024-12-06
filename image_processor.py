import os
import base64
from datetime import datetime
from dotenv import load_dotenv
from typing import Union, List, Tuple


load_dotenv()
DEBUG = os.environ.get('DEBUG')
static_url = os.environ.get('static_url')
upload_folder = os.environ.get("upload_folder")


def get_py_stamp(js_timestamp: str):
    """ Converts js timestamp to python timestamp

    Args:
        js_timestamp (str): JS timestamp in format: "dd/mm/yyyy, hh:mm:ss AM/PM"

    Returns:
        str: Python timestamp in format: "yyyy-mm-dd_hh-mm-ss"
    """

    try:
        dt_timestamp = datetime.strptime(js_timestamp, "%d/%m/%Y, %I:%M:%S %p")
        py_timestamp = dt_timestamp.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        return py_timestamp
    except ValueError as e:
        raise ValueError(f"Invalid JS timestamp format: {js_timestamp}") from e


def process_image(
        timestamps: Union[List[str], str],
        base64s: Union[List[str], str]
) -> Tuple[List[str], List[str], List[str]]:
    """
    Takes js timestamps and base64s
    Converts into py stamps, and also, saves the images
    Returns modified js stamps with _1, _2 etc. as well

    Args:
        timestamps (Union[list, str]): List of timestamps in format: "dd/mm/yyyy, hh:mm:ss AM/PM"
        base64s (Union[list, str]): List of base64 strings

    Returns:
        Tuple of:
        - List: List of file names
        - List: List of python timestamps
        - List: List of modified js timestamps
    """

    if isinstance(timestamps, str):
        timestamps = [timestamps]
    if isinstance(base64s, str):
        base64s = [base64s]

    if DEBUG:
        print(f"[Img-processor Info]: Got {len(base64s)} images and {len(timestamps)} timestamps...")

    if len(timestamps) != len(base64s):
        raise ValueError(
            "Mismatched lengths: timestamps and base64 strings must have the same number of elements.")

    curr_stamp = datetime.now()
    py_time_stamps = []
    js_modified_time_stamps = []
    file_names = []

    # Issues is that, when multiple frames under same second are passed, our naming scheme does not support that. The same name is returned by function and only one image is over-written again n again with that PARTICULAR name.
    # So keeping the last saved name in memory to add some _1, _2 after the repeated names.
    last_saved = ""
    same_name_count = 0

    # with open("formData.json", 'w') as f:
    #     f.write(json.dumps({'timestamps': timestamps, 'bases': base64s}))

    for idx, (timestamp, base64_str) in enumerate(zip(timestamps, base64s)):
        try:
            # get the extension from: "data:image/jpeg;base64,full_base64_string"
            base64_split = base64_str.split(',')
            extension = base64_split[0].split('/')[1].split(';')[0]
            # remove that part: "data:image/jpeg;base64"
            image_data = base64.b64decode(base64_split[1])

            # Create subfolder for current session:
            # "uploads/curr_timestamp_folder/all_images_in_that_session"
            subfolder = f'{curr_stamp.strftime("%Y-%m-%d_%Hh%Mm%Ss")}'
            folder = os.path.join(static_url, upload_folder, subfolder)
            os.makedirs(folder, exist_ok=True)

            # Generate unique file name
            file_base_name = get_py_stamp(timestamp)
            if file_base_name == last_saved:
                same_name_count += 1
                file_base_name += f'_{same_name_count}'
            else:
                last_saved = file_base_name
                same_name_count = 0

            file_name = f'{file_base_name}.{extension}'
            file_path = os.path.join(folder, file_name)

            # Save the image to the specified path
            with open(file_path, 'wb') as f:
                f.write(image_data)

            file_names.append(file_path)
            py_time_stamps.append(file_base_name)
            js_modified_time_stamps.append(f"{timestamp}, {same_name_count}")

        except base64.binascii.Error as e:
            print(f"[Img-processor Error] Invalid Base64 string at index {idx}: {e}")
        except ValueError as e:
            print(f"[Img-processor Error] Timestamp processing failed at index {idx}: {e}")
        except Exception as e:
            print(f"[Img-processor Error] Failed to process image at index {idx}: {e}")

        if DEBUG:
            print(f'[Img-processor Info]: Saved image `{file_name}` successfully...')

    return file_names, py_time_stamps, js_modified_time_stamps


# Example usage:
# DEBUG = True
# timestamps = ["01/12/2024, 12:30:45 PM", "01/12/2024, 12:30:46 PM"]
# base64s = [
#     "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAFiUAABYlAUlSJPAAAABSSURBVChTY3gro/IfjpWU////xICCqaDguYLqfzhWU/n/4wM7CmZQ2ujzH4YVNwb+Z1j88j/DklcQGoQxFIAkYRirApgJOBUsegGRANGLXvwHAMqqnG+1iY7uAAAAAElFTkSuQmCC",
#     "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAFiUAABYlAUlSJPAAAAA5SURBVChTY2RgYPgPxHDw/9dPKAsCmKA0TkCOApCtCMwyqX82SBQM/v37x8DIxgblQQBN3IAMGBgAKtgIyljaekYAAAAASUVORK5CYII=",
# ]
# process_image(timestamps, base64s)