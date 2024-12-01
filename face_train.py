import os
import pickle
import face_recognition

# Declare the image file name
image_name = "person.jpg"  # Replace with your image file name
pickle_name = "person_model.pkl"  # Output pickle file name

try:
    # Load the image
    print(f"Loading image: {image_name}")
    open_img = face_recognition.load_image_file(image_name)

    # Encode the face
    print("Encoding face...")
    face_encoding = face_recognition.face_encodings(open_img)[0]

    # Save the encoded face to a pickle file
    print(f"Saving model to: {pickle_name}")
    with open(pickle_name, "wb") as f:
        pickle.dump(face_encoding, f)
        print("Model saved successfully!")

except Exception as e:
    print(f"Error: {e}")
