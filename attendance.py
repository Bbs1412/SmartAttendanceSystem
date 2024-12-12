import os
import cv2
import json
import pickle
import threading
import numpy as np
import face_recognition
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Initialize locks
register_lock = threading.Lock()

# Timer class to calculate time taken by any processes


class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.time_diff = None

    def start(self):
        self.start_time = datetime.now()

    def end(self):
        self.end_time = datetime.now()
        self.time_diff = (self.end_time - self.start_time).total_seconds()

    def get_diff(self):
        return self.time_diff

    def get_json(self, start_name='start_time', end_name='end_time', diff_name='time_diff'):
        return {
            start_name: self.start_time.strftime("%d/%m/%Y, %I:%M:%S %p"),
            end_name: self.end_time.strftime("%d/%m/%Y, %I:%M:%S %p"),
            diff_name: self.time_diff
        }


# Logging helper functions to save logs:
logs = []


def create_log(log):
    """Creates a log and appends it to the global logs list"""
    global logs
    logs.append(log)


def export_logs():
    """Exports the logs to the json file at  once (at end of the process)"""
    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=4)


# Initialize variables for models path
models_path = 'Models/'

# Load known face encodings and student register
known_face_encodings = []
known_face_reg_no = []
student_names = []

# load the `class` json created from face modelling code (like a student register)
register_file = 'register.json'
register = {}

with open(register_file, 'r') as file:
    register_data = json.load(file)

    for stud in register_data:
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

    create_log({"log": "Loaded student register", "time": datetime.now()})
    # print(json.dumps(register, indent=4))


# Load saved face models from model pkl:
known_face_encodings = []
known_face_reg_no = []

for stud in register.keys():
    file_name = register[stud]['Pickle']
    file_path = os.path.join("models", file_name)

    with open(file_path, 'rb') as file:
        known_face_encodings.append(pickle.load(file))

    known_face_reg_no.append(register[stud]['Reg_No'])

    create_log({
        "log": f"Loaded Model: ({register[stud]['Reg_No']}) {register[stud]['Name']}",
        "time": datetime.now()}
    )
    print(
        f"Loaded Model: ({register[stud]['Reg_No']}) {register[stud]['Name']}")


# Function to check attendance for a list of images
def check_attendance(image_paths):
    present_people = []
    timer = Timer()

    for image_path in image_paths:
        timer.start()

        image = cv2.imread(image_path)
        small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding)
            face_distance = face_recognition.face_distance(
                known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distance)

            if matches[best_match_index]:
                reg_no = known_face_reg_no[best_match_index]
                name = student_names[best_match_index]
                present_people.append({"Reg_No": reg_no, "Name": name})

        timer.end()
        create_log({
            "log": f"Processed {image_path} in {timer.get_diff()} seconds",
            "time": datetime.now()
        })
        print(f"Processed {image_path} in {timer.get_diff()} seconds")

    return present_people


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


# List of image paths to check attendance
image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']

# Call the function to check attendance
present = check_attendance(image_paths)
create_log({"log": f"Present students: {present}", "time": datetime.now()})
print("Present students:", present)

# Export logs to json file
export_logs()
