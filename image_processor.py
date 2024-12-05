import os
import base64
from datetime import datetime
from dotenv import load_dotenv
from typing import Union, List


load_dotenv()
static_url = os.environ.get('static_url')
upload_folder = os.environ.get("upload_folder")


def get_py_stamp(js_timestamp: str):
    """ Converts js timestamp to python timestamp

    Args:
        js_timestamp (str): JS timestamp in format: "dd/mm/yyyy, hh:mm:ss AM/PM"

    Returns:
        str: Python timestamp in format: "yyyy-mm-dd_hh-mm-ss"
    """

    dt_timestamp = datetime.strptime(js_timestamp, "%d/%m/%Y, %I:%M:%S %p")
    py_timestamp = dt_timestamp.strftime("%Y-%m-%d_%Hh%Mm%Ss")
    return py_timestamp


def process_image(timestamps: Union[list, str], base64s: Union[list, str]):
    """
    Takes js timestamps and base64s
    Converts into py stamps, and also, saves the images
    Returns modified js stamps with _1, _2 etc. as well

    Args:
        timestamps (Union[list, str]): List of timestamps in format: "dd/mm/yyyy, hh:mm:ss AM/PM"
        base64s (Union[list, str]): List of base64 strings

    Returns:
        List: List of file names
        List: List of python timestamps
        List: List of modified js timestamps
    """

    curr_stamp = datetime.now()
    py_time_stamps = []
    js_modified_time_stamps = []
    file_names = []

    # Issues is that, when multiple frames under same second are passed, our naming scheme does not support that
    # Means, the same name is returned by function and only one image is over-written again n again with that PARTICULAR name.
    # So keeping the last saved name in memory to add some _1, _2 after the repeated names.
    last_saved = ""
    same_name_count = 0

    # with open("formData.json", 'w') as f:
    #     f.write(json.dumps({'timestamps': timestamps, 'bases': base64s}))

    for timestamp, base64_str in zip(timestamps, base64s):
        # get the extension from: "data:image/jpeg;base64,full_base64_string"
        extension = base64_str.split(',')[0].split('/')[1].split(';')[0]
        # remove that part: "data:image/jpeg;base64"
        image_data = base64.b64decode(base64_str.split(',')[1])

        # Uploads/curr_timestamp_folder/all_images_in_that_session
        subfolder = f'{curr_stamp.strftime("%Y-%m-%d_%Hh%Mm%Ss")}'
        folder = os.path.join(static_url, upload_folder, subfolder)
        os.makedirs(folder, exist_ok=True)

        file_base_name = get_py_stamp(timestamp)

        if file_base_name == last_saved:
            same_name_count += 1
            file_base_name += f'_{same_name_count}'
        else:
            last_saved = file_base_name
            same_name_count = 0

        file_name = f'{file_base_name}.{extension}'
        file_path = os.path.join(folder, file_name)

        file_names.append(file_path)
        py_time_stamps.append(file_base_name)
        js_modified_time_stamps.append(f"{timestamp}, {same_name_count}")

        with open(file_path, 'wb') as f:
            f.write(image_data)

        # print(f'Saved image `{file_name}` successfully...')
    return file_names, py_time_stamps, js_modified_time_stamps
# process_image(timestamps, )
