import os
import cv2
import json
import pickle
import threading
import numpy as np
import face_recognition
from datetime import datetime
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor


# ================================================================================
# Loading all the required paths and files:
# ================================================================================

load_dotenv()
static_url = os.environ.get('static_url')
attendance_log_path = os.environ.get("attendance_log_file")
class_attendance_path = os.environ.get('class_attendance')
class_register_path = os.environ.get('class_register')

attendance_log_file = os.path.join(static_url, attendance_log_path)
class_attendance_file = os.path.join(static_url, class_attendance_path)
class_register_file = os.path.join(static_url, class_register_path)

# Initialize locks
register_lock = threading.Lock()


# ================================================================================
# load the `class` json created from face modelling code (like a student register)
# ================================================================================

with open(class_register_file, 'r') as file:
    tmp = json.load(file)
# print(json.dumps(tmp, indent=4))

# modify it to have all required things of actual register
register = {}
for stud in tmp:
    register[stud['Reg_No']] = {
        'Name': stud['Name'],
        'Reg_No': stud['Reg_No'],
        "Disp_name": stud['Disp_name'],
        "Image": stud['Image'],
        "Pickle": stud['Pickle'],

        "First_In": -1,
        "Last_In": -1,
        "Attendance": {},
        "Percentage": -1,
        "Status": -1,
    }
# print(json.dumps(register, indent=4))


# ================================================================================
# Load saved face models from model pkl:
# ================================================================================


known_face_encodings = []
known_face_reg_no = []

for stud in register.keys():
    file_name = register[stud]['Pickle']
    file_path = os.path.join(static_url, "models", file_name)

    with open(file_path, 'rb') as file:
        known_face_encodings.append(pickle.load(file))

    known_face_reg_no.append(register[stud]['Reg_No'])
    print(
        f"Loaded Model: ({register[stud]['Reg_No']}) {register[stud]['Name']}")


# ================================================================================
# Timer class to calculate time taken by any of the threads/processes etc.:
# ================================================================================

class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.time_diff = None

    def start(self):
        # self.start_time = time.time()
        self.start_time = datetime.now()

    def end(self):
        # self.end_time = time.time()
        self.end_time = datetime.now()
        self.time_diff = (self.end_time - self.start_time).total_seconds()

    def get_diff(self):
        return self.time_diff

    def get_json(self, start_name='start_time', end_name='end_time', diff_name='time_diff'):
        # outputs are in this format: "start_time"="2024-11-23T17:21:30.216641",
        # return {
        #     start_name: self.start_time.isoformat(),
        #     end_name: self.end_time.isoformat(),
        #     diff_name: self.time_diff
        # }

        # I want start and end times in this format: "23/11/2024, 5:21:04 pm"
        return {
            start_name: self.start_time.strftime("%d/%m/%Y, %I:%M:%S %p"),
            end_name: self.end_time.strftime("%d/%m/%Y, %I:%M:%S %p"),
            diff_name: self.time_diff
        }

    def help(self):
        _help = """
            To use this Timer class, do the following:
            1. Create an object of Timer class
                t = Timer()
            2. Start the timer:
                t.start()
            3. End the timer:
                t.end()
            4. Get the time difference:
                t.get_time_diff()
            5. Get the time records in json format:
                t.get_json()
            6. To save json:
                with open("time.json", "w") as f:
                json.dump(t.get_json(), f, indent=4)
            *** That's it! ***
        """
        print(_help)
        return _help



# ================================================================================
# Actual code which checks the attendance, given a frame/image:
# ================================================================================

def check_attendance(frame: str) -> list:
    """
    Function which takes just one image_path and returns the reg_no of present people

    Args:
        frame (str | list): path of the file

    Returns:
        list: list with reg no of present people
    """

    video_capture = cv2.VideoCapture(frame)
    # video_capture = cv2.imread(frame)

    # Frame pre-processing:
    _, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

    # get the locations where faces are recognized:
    face_locations = face_recognition.face_locations(rgb_small_frame)

    # get the encodings of those recognized faces:
    face_encodings = face_recognition.face_encodings(
        face_image=rgb_small_frame,
        known_face_locations=face_locations,
        num_jitters=1
    )

    # ------------------------------------------------------------------------
    present_people = []

    # for all the faces found in this image/frame:
    for face_encoding in face_encodings:

        # get a list of true/false for match-found with all the known encodings:
        matches = face_recognition.compare_faces(
            known_face_encodings=known_face_encodings,
            face_encoding_to_check=face_encoding
        )

        # this returns list of distances with all the known encodings
        face_distance = face_recognition.face_distance(
            face_encodings=known_face_encodings,
            face_to_compare=face_encoding
        )

        # find the person with minimum dist (best match):
        best_match_index = np.argmin(face_distance)
        # later this will be also cross checked with matches list [True/False]
        # Then declared as present or not finally

        # if that minimum dist image exists in matches as True, then mark present:
        if matches[best_match_index] == True:
            reg_no = known_face_reg_no[best_match_index]
            present_people.append(reg_no)

    video_capture.release()
    cv2.destroyAllWindows()
    return present_people


# ================================================================================
# Logging helper functions to save logs:
# ================================================================================

# To solve the concurrency issues with file-write,
# I am just appending the logs in one list, then, will save all at once:
logs = []


def create_log(log):
    """Creates a log and appends it to the global logs list"""
    global logs
    logs.append(log)


def export_logs():
    """Exports the logs to the json file at  once (at end of the process)"""
    with open(attendance_log_file, "w") as f:
        json.dump(logs, f, indent=4)
        # json.dump(logs, f)



def get_datetime(js_mod_dt):
    "Gives the frame number and datetime in datetime (python)'s std format"
    # sample = "8/8/2024, 12:56:36 am, 0"
    number = js_mod_dt.split(",")[-1].strip()
    stamp = ', '.join(js_mod_dt.split(",")[:-1])
    dt_timestamp = datetime.strptime(stamp, "%d/%m/%Y, %I:%M:%S %p")

    # print(f'Stamp: {stamp.center(25)} & Number: {str(number).center(4)}', end='\r')
    return dt_timestamp, int(number)


def update_register(present, timestamp):
    with register_lock:
        for reg_no in register.keys():
            # remove image and pickle (server side) details:
            register[reg_no].pop('Image', None)
            register[reg_no].pop('Pickle', None)

            if reg_no in present:
                register[reg_no]['Attendance'][timestamp] = True

                # If first_in is not init, then put the curr stamp,
                # else, compare and keep older stamp...
                if register[reg_no]['First_In'] == -1:
                    register[reg_no]['First_In'] = timestamp
                else:
                    # curr stamp
                    curr_dt, curr_frame = get_datetime(timestamp)
                    # saved stamp
                    saved_dt, saved_frame = get_datetime(
                        register[reg_no]['First_In'])

                    # if curr dt came earlier or the frame number is smaller than saved one within the same dt stamp
                    if (curr_dt < saved_dt) or (curr_dt == saved_dt and curr_frame < saved_frame):
                        register[reg_no]['First_In'] = timestamp

                # If last_in is not init, then put the curr stamp,
                # else, compare and keep newer stamp...
                if register[reg_no]['Last_In'] == -1:
                    register[reg_no]['Last_In'] = timestamp
                else:
                    # curr stamp
                    curr_dt, curr_frame = get_datetime(timestamp)
                    # saved stamp
                    saved_dt, saved_frame = get_datetime(
                        register[reg_no]['Last_In'])

                    # if curr dt came later or the frame number is larger than saved one within the same dt stamp
                    if (curr_dt > saved_dt) or (curr_dt == saved_dt and curr_frame > saved_frame):
                        register[reg_no]['Last_In'] = timestamp

            else:
                register[reg_no]['Attendance'][timestamp] = False


# Check attendance for each image and update the register
def check_image(args):
    i, to_check, timestamp = args
    timer = Timer()
    timer.start()
    present = check_attendance(to_check[i])
    timer.end()

    timer_for_lock = Timer()
    timer_for_lock.start()
    update_register(present, timestamp[i])
    timer_for_lock.end()

    time_records = {}
    time_records = timer.get_json(
        start_name='thread_start_time',
        end_name='thread_end_time',
        diff_name='thread_time_taken'
    )
    time_records['register_lock_time'] = timer_for_lock.get_diff()
    create_log({
        'timestamp': timestamp[i],
        'time_records': time_records,
        'people_present': present,
    })


# Driver function to check attendance for multiple images
def driver_function(to_check: list, timestamp: list):
    timer_ = Timer()
    timer_.start()

    # max_workers = 5
    max_workers = os.cpu_count()

    # with ThreadPoolExecutor(max_workers=max_workers) as executor:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(check_image, [(i, to_check, timestamp)
                     for i in range(len(to_check))])

    timer_.end()
    create_log({'title': 'final log', **timer_.get_json(
        start_name='calc_start_time',
        end_name='calc_end_time',
        diff_name='calc_time_taken'
    )})
    export_logs()


# Function to mark attendance and save the register
def mark_attendance():
    for stud in register.keys():
        stud = register[stud]
        present = 0
        absent = 0

        # iterate over all the time-stamps:
        for stamp in stud['Attendance'].keys():
            # print(stud['Attendance'][stamp])
            if (stud['Attendance'][stamp]):
                present += 1
            else:
                absent += 1

        percentage = round((present / (present + absent)) * 100)
        stud['Percentage'] = percentage
        status = 'Present' if percentage >= 75 else 'Absent'
        stud['Status'] = status

        # print(f'Present: {present}, Absent: {absent}')
        # print(f'Status: {status}, Percentage: {percentage}')


# Save the register to a json file
def save_register():
    mark_attendance()

    json_file = os.environ.get('class_attendance')
    with open(json_file, "w") as f:
        json.dump(register, f, indent=4)


# List of image paths to check attendance
image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']

# Call the function to check attendance
present = check_attendance(image_paths)
create_log({"log": f"Present students: {present}", "time": datetime.now()})
print("Present students:", present)

# Export logs to json file
export_logs()
