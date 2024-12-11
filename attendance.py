import os
import cv2
import json
import pickle
import numpy as np
import face_recognition
from datetime import datetime


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


# List of image paths to check attendance
image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']

# Call the function to check attendance
present = check_attendance(image_paths)
create_log({"log": f"Present students: {present}", "time": datetime.now()})
print("Present students:", present)

# Export logs to json file
export_logs()
