import os
import time
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from attendance import save_register
from attendance import driver_function
from image_processor import process_image

from werkzeug.exceptions import RequestEntityTooLarge
from flask import (Flask, render_template, request,
                   send_file, send_from_directory, jsonify)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Max file size limit:
MB = 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = 50 * MB

# Global variables
load_dotenv()
static_url = os.environ.get('static_url')

# Just initializing the variable, will be updated in the upload_video route
no_of_frames_recvd = 20
js_timestamps, py_timestamps, js_mod_timestamps = [], [], []
file_names = []
processing_complete = False

for folders in [os.environ.get('upload_folder'), os.environ.get('excel_folder')]:
    os.makedirs(os.path.join(static_url, folders), exist_ok=True)


# @app.route('/testing', methods=('POST',))
# def view_post():
#     return request.data


# Test route to check if the server is running:
@app.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'success', 'message': 'Server is running!!'}), 200


# Route to render the index.html template (home page)
@app.route('/')
def index():
    return render_template('index.html')


# Route to serve the assets (CSS, JS, images, etc.)
@app.route('/assets/<path:filename>')
def send_asset(filename):
    # Ensure the directory you want to serve files from is secure and within the application's directory
    # path = os.path.join(static_url, "Templates",'assets', filename)
    return send_from_directory('assets', filename)


# Route to upload the video data and process the images:
@app.route('/upload_video', methods=['POST'])
def upload_video():
    t1 = time.time()

    content_length = request.content_length  # Total request size in bytes
    print(f"Total request size: {content_length} bytes")  # or use logging

    # You can also check the headers directly:
    print(f"Request Headers: {request.headers}")

    global no_of_frames_recvd, js_timestamps, py_timestamps, file_names, js_mod_timestamps

    # print(request.form)
    sample_of_this_data = """
    ImmutableMultiDict([
        ('num_students', '2'),
        ('student_names', 'B, V'),
        ('video_data', '["data:image/jpeg;base64,/9j/4AAQSkZ...
    """

    # extract required data from the form response:
    frames_data = request.form.get('video_data')
    timestamps = request.form.get('timestamps')

    # if no video captured:
    if not frames_data:
        return jsonify({'status': 'error',
                        'message': 'No video data received'}), 400

    # convert the string (get/post) response into list
    frames = eval(frames_data)
    no_of_frames_recvd = len(frames)

    # get the timestamps str response -> list
    js_timestamps = eval(timestamps)
    file_names, py_timestamps, js_mod_timestamps = process_image(
        js_timestamps, frames)

    file = os.path.join(static_url, os.environ.get('uploaded_data'))

    with open(file, 'w') as f:
        json.dump({'files': file_names,
                   'py': py_timestamps,
                   'js': js_timestamps,
                   'js_mod': js_mod_timestamps, }, f, indent=4)

    t2 = time.time()
    return jsonify({'status': 'success',
                    'message': 'Image processing completed!!',
                    'time': f'{round(t2-t1, 4)} secs!'}), 200


# Route to start attendance calculation on server:
@app.route('/calc_attendance', methods=['GET'])
def calc_attendance():
    t1 = time.time()
    driver_function(file_names, js_mod_timestamps)
    save_register()
    t2 = time.time()

    return jsonify({"status": "completed",
                    "response": "Attendance calculation successful",
                    'time': f'{round(t2-t1, 3)} secs'
                    }), 200


# Route to get the final attendance data (result):
@app.route('/results', methods=['GET'])
def results():
    # Load attendance data from JSON file
    path = os.path.join(os.environ.get('static_url'),
                        os.environ.get('class_attendance'))
    with open(path, 'r') as file:
        register = json.load(file)

    # Update attendance data with extracted time
    for student_id, details in register.items():
        # Extract time for "First_In" and "Last_In" if available
        details['First_In'] = extract_time(details['First_In'])
        details['Last_In'] = extract_time(details['Last_In'])

    # Pass the attendance register to the template
    # Pick whatever data you want to display in the results page {{ using this }}
    return render_template('results.html', register=register), 200


# Save attendance data to Excel with timestamped filename:
@app.route('/download')
def download_excel():
    # Load attendance data from JSON file
    path = os.path.join(static_url, os.environ.get('class_attendance'))
    with open(path, 'r') as file:
        register = json.load(file)

    # Convert the attendance register to a DataFrame
    data = []
    for reg_no, details in register.items():
        info = {
            'Reg No': reg_no,
            # 'Reg No': details['Reg No'],
            'Name': details['Name'],
            'In Time': extract_time(details['First_In']),
            'Out Time': extract_time(details['Last_In']),
            'Percentage': details['Percentage'],
            'Status': details['Status']
        }

        data.append(info)

    df = pd.DataFrame(data, columns=data[0].keys())

    file_name = f'{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.xlsx'
    file_path = os.path.join(
        static_url, os.environ.get('excel_folder'), file_name)

    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)


# Error handler for RequestEntityTooLarge
@app.errorhandler(RequestEntityTooLarge)
def handle_413_error(error):
    return jsonify("The file you uploaded is too large. Please try again with a smaller file."), 413


# ======================================================================
# Some helper functions:
# ======================================================================


# Function to extract the time by splitting the string
def extract_time(date_time_string):
    try:
        # If the input is an integer, return "N/A"
        if isinstance(date_time_string, int):
            return "N/A"

        # Split by comma and extract the second element (the time)
        return date_time_string.split(',')[1].strip()
    except (IndexError, AttributeError):
        # Catch IndexError (for missing commas) or AttributeError (if input is not a string)
        return "N/A"


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
    )
