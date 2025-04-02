# Standard library imports
import os
import PySimpleGUI as sg
from PIL import Image
from os.path import exists

# Local imports
from .image_loader import image_open
from .color_palette import clear_color_palette

# Add to top of file if not already present
TEMP_PNG = "tmp.png"

# Function to validate file type
def is_valid_file_type(file_path):
    valid_extensions = ('.gif', '.jpg', '.png', '.pcx', '.bmp')
    return file_path.lower().endswith(valid_extensions)

# Function to handle file loading
def handle_file_load(file_path, file_list, window, image_open, clear_color_palette_fn):
    """Handle loading a file into the application.
    
    Args:
        file_path (str): Path to the file to load
        file_list (list): List of loaded files
        window: The PySimpleGUI window instance
        image_open (callable): Function to open and process the image
        clear_color_palette_fn (callable): Function to clear color palette display
        
    Returns:
        tuple: (file_path, full_image, color_palette, image_dimensions) or (None, None, None, None)
    """
    if os.path.exists(file_path):
        file_list.append(file_path)
        window["-FILE LIST-"].update(file_list)
        full_image, color_palette, image_dimensions = image_open(file_path)
        clear_color_palette_fn(file_path)
        return file_path, full_image, color_palette, image_dimensions
    return None, None, None, None

# Function to display error popup
def show_error_popup(message, font):
    sg.Popup(message, font=font, button_type=5, title="Error!")

# Function to convert an image to RGB
def convert_to_RGB(current_image, output_path=TEMP_PNG):
    """Convert any image file to RGB format and save as PNG.
    
    Args:
        current_image (str): Path to input image
        output_path (str): Path to save converted image (default: tmp.png)
        
    Returns:
        None
    """
    file_name = os.path.basename(current_image)
    file_ext = file_name.split(".")[1].lower()
    
    if file_ext == "png":
        # Handle PNG with alpha channel
        png = Image.open(current_image).convert('RGBA')
        png.load()  # Required for png.split()
        background = Image.new("RGB", png.size, (255, 255, 255))
        background.paste(png, mask=png.split()[3])
        background.save(output_path, 'PNG')
    elif file_ext != "pcx":
        # Handle other image formats
        image = Image.open(current_image)
        RGB_image = image.convert("RGB") 
        RGB_image.save(output_path)

def delete_file(file_name):
    """Delete a file if it exists.
    
    Args:
        file_name (str): Path to the file to delete
    """
    file_exists = exists(file_name)
    if file_exists:  
        os.remove(file_name)
