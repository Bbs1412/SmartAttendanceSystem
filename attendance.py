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


# Initialize variables for models path
models_path = 'Models/'

# Load known face encodings and student register
known_face_encodings = []
known_face_reg_no = []
student_names = []

# Load register from register.json
register_file = 'register.json'

with open(register_file, 'r') as file:
    register_data = json.load(file)

    for student in register_data:
        reg_no = student["Reg_No"]
        student_name = student["Name"]
        # Path to the pickle file
        pickle_file = models_path + student["Pickle"]
        # Load the pickle file
        with open(pickle_file, 'rb') as pf:
            face_encoding = pickle.load(pf)
            known_face_encodings.append(face_encoding)
            known_face_reg_no.append(reg_no)
            student_names.append(student_name)


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
        print(f"Processed {image_path} in {timer.get_diff()} seconds")

    return present_people


# List of image paths to check attendance
image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']

# Call the function to check attendance
present = check_attendance(image_paths)
print("Present students:", present)
