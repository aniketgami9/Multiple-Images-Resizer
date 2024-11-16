# app.py

import os
from PIL import Image, ImageOps
import logging
from concurrent.futures import ThreadPoolExecutor

# Configuration
config = {
    "background_color": (255, 255, 255),  # Background color (white by default)
    "output_format": "JPEG",  # Output format (e.g., "PNG", "JPEG")
    "max_threads": 4,  # Number of threads for parallel processing
}

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

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

def process_image(filename, input_folder, output_folder, target_width, target_height):
    """
    Process a single image: resize, pad, and save.
    """
    input_path = os.path.join(input_folder, filename)
    output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.{config['output_format'].lower()}")
    
    try:
        with Image.open(input_path) as img:
            resized_img = resize_and_pad(img, target_width, target_height, config["background_color"])
            resized_img.save(output_path, config["output_format"])
            logger.info(f"Processed and saved: {output_path}")
    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")

def main():
    """
    Main function to process images.
    """
    # Get user input for the input folder
    input_folder = input("Enter the path to the input folder: ").strip()
    
    # Validate the input folder
    if not os.path.isdir(input_folder):
        logger.error(f"The specified input folder does not exist: {input_folder}")
        return
    
    # Get user input for the target dimensions
    try:
        target_width = int(input("Enter the target width of the image: ").strip())
        target_height = int(input("Enter the target height of the image: ").strip())
    except ValueError:
        logger.error("Invalid input for dimensions. Please enter integers.")
        return
    
    # Define the output folder inside the input folder
    output_folder = os.path.join(input_folder, "Processed")
    os.makedirs(output_folder, exist_ok=True)
    
    # Find all valid image files in the input folder
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not files:
        logger.warning("No images found in the input folder.")
        return
    
    logger.info(f"Found {len(files)} images. Starting processing...")
    
    # Process images using multithreading
    with ThreadPoolExecutor(max_workers=config["max_threads"]) as executor:
        executor.map(lambda f: process_image(f, input_folder, output_folder, target_width, target_height), files)
    
    logger.info(f"Processing complete! Processed images are saved in: {output_folder}")

if __name__ == "__main__":
    main()
