import cv2
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


# Initialize variables for image and models path
image_path = 'path_to_image.jpg'
models_path = 'Models/'

# Load known face encodings from pickle files
known_face_encodings = []
known_face_reg_no = []

# Load the saved model
file_path = models_path + 'student_model.pkl'
with open(file_path, 'rb') as file:
    known_face_encodings.append(pickle.load(file))


# Function to check attendance for a given image
def check_attendance(image_path):
    timer = Timer()
    timer.start()

    image = cv2.imread(image_path)
    small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(
        rgb_small_frame, face_locations)

    present_people = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(
            known_face_encodings, face_encoding)
        face_distance = face_recognition.face_distance(
            known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distance)

        if matches[best_match_index]:
            reg_no = known_face_reg_no[best_match_index]
            present_people.append(reg_no)

    timer.end()
    print(f"Time taken: {timer.get_diff()} seconds")

    return present_people


# Call the function to check attendance
present = check_attendance(image_path)
print("Present students:", present)
