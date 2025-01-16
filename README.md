# Smart Attendance System
The Smart Attendance System automates attendance calculation during lectures using a video uploaded through a user-friendly interface. The system processes the video frames with OpenCV, identifies students using pre-trained face encodings, and calculates attendance based on a threshold of 75% frame presence. It ensures concurrency with threading and provides results in a downloadable Excel format.


## Index:
- [Smart Attendance System](#smart-attendance-system)
- [Project Details](#-project-details)
    - [Aim](#aim)
    - [Methodology](#methodology)
    - [Features](#features)
    - [Tech Stack](#tech-stack)
- [Steps to run](#-steps-to-run)
- [Extra Measures](#ℹ️-extra-measures)
    - [General Instructions](#general-instructions)
    - [Folders](#folders)
    - [Template Rendering Errors](#template-rendering-errors)
- [Contributions](#-contributions)
- [License](#-license)
- [Contact](#-contact)


## 🎯 Project Details:
### Aim:
To automate attendance calculation efficiently using face recognition, ensuring accuracy and convenience for faculty and students.

### Methodology:
+ Video is pre-processed and uploaded from the frontend and sent to a Flask server.
+ Frames are processed using OpenCV for face recognition.
+ Captured `face Locations` are compared against pre-saved encodings using `face distance` and `face encodings` to identify individuals.
+ Face encodings are a one-time process completed during registration of new student.
+ Attendance is calculated based on frame presence with a threshold of 75%.
+ Results are rendered on a webpage and made downloadable in Excel format.

### Features:
+ Upload video for attendance processing.
+ Real-time face recognition with concurrency using threading, locking for consistent read-write operations.
+ Faster operation and time-saving due to parallel processing. 
+ Threshold-based attendance marking for customizable and accurate results.
+ Faculty access to detailed results and downloadable attendance records.
+ Web-based interface for ease of use.

### Tech Stack:
+ **Backend:** Python, Flask
+ **Frontend:** HTML, CSS, JavaScript
+ **Libraries:** OpenCV, face_recognition, threading
+ **Data Formats:** JSON, Excel
+ **Tools:** Virtual environment (venv), Python's standard libraries


## 🚀 Steps to run:

1. Clone the repository:
    ```bash
    git clone --depth 1 https://github.com/Bbs1412/SmartAttendanceSystem
    ```
    
1. Navigate to the project directory:
    ```bash
    cd SmartAttendanceSystem
    ```

1. Create a virtual environment:
    ```bash
    python -m venv venv
    ```

1. Activate the virtual environment:
    - Windows
        ```bash
        venv\Scripts\activate
        ```
    - Linux
        ```bash
        source venv/bin/activate
        ```

1. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

1. Set the environment variables (Optional):
    - Open the `.env` file and update the environment variables if needed or keep the default values

1. Adding the images:
    - Create a folder named `Pics` in the project directory
        ```bash
        mkdir Pics
        ```
    - Add the images of the people you want to recognize in the `Pics` folder.
    
1. Train the models:
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

1. Run the app:
    ```bash
    python app.py
    ```

1. Open the browser and go to the following URL (default):
    ```URL
    http://localhost:5000
    ```


## ℹ️ Extra Measures:

### General Instructions:
- Using Conda for environment creation may help ease the process and might make it faster.
- If some errors occurs:
    1. First try deleting the `__pycache__` folder
    1. Restart the server and run the application again.

### Folders:
- Although the code includes conditions to dynamically check and resolve issues, if an error occurs or for re-verification, please check the following folders:
    | Folder | Detail | Checking |
    | --- | --- | --- |
    | `assets/` | Should contain all the css, js, images, etc. | Cloned from repository |
    | `Templates/` | Should contain all the html files | Cloned from repository |
    | `Pics/` | Should contain all the images of people to be recognized | Must be done by user |
    | `Excels/` | Empty initially | Dynamically Checked in `app.py` |
    | `Uploads/` | Empty initially | Dynamically Checked in `image_processor.py` |
    | `Jsons/` | Empty initially | Dynamically Checked in `face_train.py` |
    | `Models/` | Empty initially | Dynamically Checked in `face_train.py` |
    | `.env` | (File) Should contain all the environment variables | Cloned from repository |
- In case you have changed the env variables, check folders accordingly

### Template Rendering Errors:
- `Templates/` might give some error on linux, check the 'T' being either capital or small
- Or else, Set the Templates folder path in the `app.py` file manually:
    ```Python
    app = Flask(__name__, template_folder='Templates')
    ```


## 🤝 Contributions:
   Any contributions or suggestions are welcome! 


## 📜 License: 
[![Code-License](https://img.shields.io/badge/License%20-GNU%20--%20GPL%20v3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
- This project is licensed under the `GNU General Public License v3.0`
- See the [LICENSE](LICENSE) file for details.
- You can use the code with proper credits to the author.


## 📧 Contact:
- **Email -** [bhushanbsongire@gmail.com](mailto:bhushanbsongire@gmail.com)
