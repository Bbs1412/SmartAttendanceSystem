import os
import base64
from datetime import datetime

# Inputs
base64_string = input("Enter the Base64 string: ")
timestamp = input("Enter timestamp (dd/mm/yyyy, hh:mm:ss AM/PM): ")

# Folder and file handling
curr_stamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
output_folder = os.path.join("uploads", curr_stamp)
os.makedirs(output_folder, exist_ok=True)

# Extract file extension dynamically
try:
    extension = base64_string.split(",")[0].split("/")[1].split(";")[0]
    image_data = base64.b64decode(base64_string.split(",")[1])

    # Generate filename from timestamp
    dt_timestamp = datetime.strptime(timestamp, "%d/%m/%Y, %I:%M:%S %p")
    py_timestamp = dt_timestamp.strftime("%Y-%m-%d_%Hh%Mm%Ss")
    output_file = f"{py_timestamp}.{extension}"

    output_path = os.path.join(output_folder, output_file)
    with open(output_path, "wb") as f:
        f.write(image_data)
    print(f"Image saved successfully at: {output_path}")
except Exception as e:
    print(f"Failed to process the image: {e}")
