# Smart Attendance System
Smart Attendance System to automate the attendance calculation in lectures using Python

## Description
- Read the todo.txt once
- Parallelized calc for attendance

## Remember:
- in the git clone command, add the `--depth 1` flag to clone only the latest commit and not the entire history
- Templates/ might give some error on linux, check the 'T' being either capital or small
- If some errors occur, first try deleting the `__pycache__` folder and then try again with server restart
- Add .env file in root directory (on github push)

## `WARNING(s):`
+ The project is not focused on implementing best security practices or showing the best ways to code something. The main aim is to integrate multiple AWS services under the free tier in the project.
+ Contributions for security or coding practices changes are welcome!!
+ If you want to add more services to the project, create a new environment variable (to enable or disable that feature/service) and add it!
+ For example, cognito service is implemented, but, it can be completely disabled by setting the its environment variable to `False` in the `.env` file. 


## Extra Measures:
- Although condition to check this dynamically are coded already, but still, if theres some error or just for reverification, check following folders:
    - assets, jsons, models, pics, Templates, 