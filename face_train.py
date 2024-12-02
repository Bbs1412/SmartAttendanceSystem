import os
import json
import pickle
import face_recognition
from dotenv import load_dotenv

load_dotenv()

# Define the paths for the models, images and jsons:
static_url = os.environ.get('static_url')
models_folder = os.environ.get('face_models_folder')
images_folder = os.environ.get('face_images_folder')
json_folder = os.environ.get('json_folder')

models_path = os.path.join(static_url, models_folder)
images_path = os.path.join(static_url, images_folder)
jsons_path = os.path.join(static_url, json_folder)

# Create the directories if not present:
os.makedirs(models_path, exist_ok=True)
os.makedirs(images_path, exist_ok=True)
os.makedirs(jsons_path, exist_ok=True)

# Path to save output JSON file for trained models as class register:
class_register_json = os.environ.get('class_register')
class_register_file = os.path.join(jsons_path, class_register_json)


class Person:
    def __init__(self, reg, name, image_name, display_name=None, pickle_name=None):
        """
        `reg:` Registration number  
        `name:` Name of person  
        `image_name:` Name of the image file (ex. 'my_name.png' only)  
        `display_name:` (Optional) Name to display (defaults to {name})  
        `pickle_name:` (Optional) Name of pickle file to create (default to {name}.pkl)  
        """
        self.RegNo = reg
        # self.name = "_".join(name.split(" "))
        self.name = name
        self.image_url = os.path.join(images_path, image_name)

        if display_name is not None:
            self.disp_name = display_name
        else:
            self.disp_name = self.name

        if pickle_name is not None:
            self.pickle_name = os.path.join(models_path, pickle_name)
        else:
            self.pickle_name = os.path.join(models_path, f"{self.name}.pkl")

    def view(self):
        def print_itm(title, detail):
            print(title.rjust(15), detail)

        print_itm("Reg No.: ", self.RegNo)
        print_itm("Name: ", self.name)
        print_itm("Disp Name: ", self.disp_name)
        print_itm("Image: ", self.image_url)
        print_itm("Pickle: ", self.pickle_name)

    def give_json(self):
        return {
            "Reg_No": self.RegNo,
            "Name": self.name,
            "Disp_name": self.disp_name,
            "Image": os.path.basename(self.image_url),
            "Pickle": os.path.basename(self.pickle_name),
        }


people = [
    # Person(reg, name, image_name(just image.jpg),
    #           (optional)display_name, (optional)pickle_name),
    Person("22CSE1234", "Bhushan Songire", "bhushan.jpg", "Bhushan", "bs.pkl"),
    Person("22CSE5678", "Another", "person.jpg", "Random", "random.pkl"),
    # add more people here...
]


class_register = []
for p in people:
    p.view()

    open_img = None
    try:
        open_img = face_recognition.load_image_file(p.image_url)
    except Exception as e:
        print("\t\t[#] Image not found, try again...", e)

    if open_img is None:
        print("\t\t[#] Skipping the model creation...")
        print()
        continue
    
    else:
        try:
            print("\t\t[#] Modelling the image...")
            face_encoding = face_recognition.face_encodings(open_img)[0]

            os.makedirs(os.path.dirname(p.pickle_name), exist_ok=True)
            with open(p.pickle_name, "wb") as f:
                pickle.dump(face_encoding, f)
                print("\t\t[#] Saved the model...")

        except Exception as e:
            print("\t\t[#] Some error occurred!", e)

    class_register.append(p.give_json())
    print()


# Define the path for the JSON file
with open(class_register_file, "w") as file:
    json.dump(class_register, file, indent=4)
print(F"Saved file: `{class_register_file}`")

print()
print("All Done!!!")
