import os
import base64

# base64 string and folder path
base64_string = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAFiUAABYlAUlSJPAAAABSSURBVChTY3gro/IfjpWU////xICCqaDguYLqfzhWU/n/4wM7CmZQ2ujzH4YVNwb+Z1j88j/DklcQGoQxFIAkYRirApgJOBUsegGRANGLXvwHAMqqnG+1iY7uAAAAAElFTkSuQmCC"

output_folder = "uploads"
output_file = "output_image.jpg"

# Create the folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Decode the base64 string and save it as an image
try:
    image_data = base64.b64decode(base64_string.split(",")[1])
    output_path = os.path.join(output_folder, output_file)

    with open(output_path, "wb") as f:
        f.write(image_data)
    print(f"Image saved successfully at: {output_path}")

except Exception as e:
    print(f"Failed to process the image: {e}")
