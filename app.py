from flask import Flask, request, render_template, redirect, url_for
import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_and_pad(image, target_width, target_height, background_color=(255, 255, 255)):
    """
    Resize an image to fit within specified dimensions with background padding.
    """
    original_width, original_height = image.size
    scale = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    new_image = Image.new("RGB", (target_width, target_height), background_color)
    paste_position = ((target_width - new_width) // 2, (target_height - new_height) // 2)
    new_image.paste(resized_image, paste_position)
    return new_image

def process_image(file_path, output_path, target_width, target_height, background_color):
    """
    Process a single image: resize, pad, and save.
    """
    try:
        with Image.open(file_path) as img:
            resized_img = resize_and_pad(img, target_width, target_height, background_color)
            resized_img.save(output_path, "JPEG")
            return True
    except Exception as e:
        app.logger.error(f"Error processing image {file_path}: {e}")
        return False

@app.route("/", methods=["GET", "POST"])
def select_and_process():
    message = ""
    message_type = "error"  # Default message type is error
    
    if request.method == "POST":
        # Get the images, dimensions, and background color from the form
        files = request.files.getlist("files")
        try:
            target_width = int(request.form["width"])
            target_height = int(request.form["height"])
            bgcolor = request.form["bgcolor"]
            # Convert the background color from Hex to RGB
            background_color = tuple(int(bgcolor[i:i+2], 16) for i in (1, 3, 5))
        except ValueError:
            message = "Invalid width, height, or background color. Please enter valid values."
            message_type = "error"
            return render_template("select.html", message=message, message_type=message_type)

        if not files:
            message = "No files selected."
            message_type = "error"
            return render_template("select.html", message=message, message_type=message_type)

        output_folder = "Processed"
        os.makedirs(output_folder, exist_ok=True)

        with ThreadPoolExecutor() as executor:
            for file in files:
                if allowed_file(file.filename):
                    file_path = os.path.join(output_folder, file.filename)
                    file.save(file_path)
                    output_path = os.path.join(output_folder, f"{os.path.splitext(file.filename)[0]}.jpeg")
                    executor.submit(process_image, file_path, output_path, target_width, target_height, background_color)

        message = f"Processing complete! Processed images are saved in: {output_folder}"
        message_type = "success"
        return render_template("select.html", message=message, message_type=message_type)

    return render_template("select.html", message=message, message_type=message_type)

if __name__ == "__main__":
    app.run(debug=True)
