# Smart Attendance System
Smart Attendance System to automate the attendance calculation in lectures using Python.


## Description
- add the Description of the project here later...


## Index:
- [Smart Attendance System](#smart-attendance-system)
- [General Instructions](#general-instructions)
- [Steps to run](#steps-to-run)
- [Extra Measures](#extra-measures)
    - [Folders](#folders)
    - [Template Rendering Errors](#template-rendering-errors)
- [Remember](#remember)
- [Contact](#contact)


## General Instructions:
- If some errors occur, first try deleting the `__pycache__` folder and then try again with server restart


## Steps to run:

1. Clone the repository
    ```bash
    git clone --depth 1 https://github.com/Bbs1412/SmartAttendanceSystem
    ```
    
1. Navigate to the project directory
    ```bash
    cd SmartAttendanceSystem
    ```

1. Create a virtual environment
    ```bash
    python -m venv venv
    ```

1. Activate the virtual environment
    - Windows
        ```bash
        venv\Scripts\activate
        ```
    - Linux
        ```bash
        source venv/bin/activate
        ```

1. Install the required packages
    ```bash
    pip install -r requirements.txt
    ```

1. Set the environment variables (Optional)
    - Open the `.env` file and update the environment variables if needed or keep the default values

1. Adding the images
    - Create a folder named `Pics` in the project directory
        ```bash
        mkdir Pics
        ```
    - Add the images of the people you want to recognize in the `Pics` folder.
    
1. Train the models
    - Open the `face_train.py` file
    - Scroll down (~ line 73) to update the ***people*** list
    - Add all the people you want to recognize in the ***people*** list by calling:
        ```Python
        Person(
            reg='registration_number',
            name='Name',
            image='person_name.jpg',      # Image should be in the 'Pics' folder
            display_name='Display Name',  # optional
            pickle_name='person_name.pkl' # optional
        )
        ```
    - Run the `face_train.py` file
        ```bash
        python face_train.py
        ```

1. Run the app
    ```bash
    python app.py
    ```


## Extra Measures:

### Folders:
- Although the code includes conditions to dynamically check and resolve issues, if an error occurs or for re-verification, please check the following folders:
    | Folder | Detail | Checking |
    | --- | --- | --- |
    | `assets/` | Should contain all the css, js, images, etc. | Cloned from repository |
    | `Templates/` | Should contain all the html files | Cloned from repository |
    | `Pics/` | Should contain all the images of people to be recognized | Must be done by user |
    | `Excels/` | Empty initially | Dynamically Checked in ?? |
    | `Uploads/` | Empty initially | Dynamically Checked in ?? |
    | `Jsons/` | Empty initially | Dynamically Checked in `face_train.py` |
    | `Models/` | Empty initially | Dynamically Checked in `face_train.py` |
- In case you have changed the env variables, check folders accordingly

### Template Rendering Errors:
- `Templates/` might give some error on linux, check the 'T' being either capital or small
- Or else, Set the Templates folder path in the `app.py` file manually:
    ```Python
    app = Flask(__name__, template_folder='Templates')
    ```


---

👇 If this still appears on Readme, please contact me 😁

---
 
## Remember:
- in the git clone command, add the `--depth 1` flag to clone only the latest commit and not the entire history
- Add .env file in root directory (on github push)
- Parallelized calc for attendance
- Add emojis in the README.md file