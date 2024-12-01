import os
import pickle
import face_recognition

# Take user inputs for image and pickle file names
image_name = input("Enter the image file name (e.g., person.jpg): ").strip()
pickle_name = input("Enter the output pickle file name (e.g., person_model.pkl): ").strip()

try:
    # Load the image
    print(f"Loading image: {image_name}")
    open_img = face_recognition.load_image_file(image_name)

    # Encode the face
    print("Encoding face...")
    face_encodings = face_recognition.face_encodings(open_img)
    if not face_encodings:
        raise ValueError("No face found in the image!")
    face_encoding = face_encodings[0]

    # Save the encoded face to a pickle file
    print(f"Saving model to: {pickle_name}")
    with open(pickle_name, "wb") as f:
        pickle.dump(face_encoding, f)
        print("Model saved successfully!")

except FileNotFoundError:
    print(f"Error: File '{image_name}' not found. Please check the file path.")
except ValueError as ve:
    print(f"Error: {ve}")
except Exception as e:
    print(f"Unexpected error: {e}")
