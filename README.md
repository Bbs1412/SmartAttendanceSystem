# Smart Attendance System
Smart Attendance System to automate the attendance calculation in lectures using Python.


## Description
- Parallelized calc for attendance


## General Instructions:
- Use depth 1 while cloning
- If some errors occur, first try deleting the `__pycache__` folder and then try again with server restart


## Extra Measures:
- Although condition to check this dynamically are coded already, but still, if theres some error or just for reverification, check following folders:
    + assets, jsons, models, pics, Templates 
- "Templates/" might give some error on linux, check the 'T' being either capital or small
- Or else, Set the Templates folder path in the `app.py` file manually:
    ```Python
    app = Flask(__name__, template_folder='Templates')
    ```


## Remember:
- in the git clone command, add the `--depth 1` flag to clone only the latest commit and not the entire history
- Add .env file in root directory (on github push)
- Parallelized calc for attendance