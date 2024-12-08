import os
import cv2
import pickle
import numpy as np
import face_recognition

# Set image path and load model
image_path = 'path_to_your_image.jpg'
model_path = 'Models/model.pkl'

# Load model
with open(model_path, 'rb') as file:
    known_face_encoding = pickle.load(file)

# Load image
image = cv2.imread(image_path)

# Preprocess image
small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

# Detect faces
face_locations = face_recognition.face_locations(rgb_small_frame)
face_encodings = face_recognition.face_encodings(
    rgb_small_frame, face_locations)

# Compare faces
for face_encoding in face_encodings:
    matches = face_recognition.compare_faces(
        [known_face_encoding], face_encoding)
    if True in matches:
        print("Face matched!")
    else:
        print("No match found.")

cv2.destroyAllWindows()
