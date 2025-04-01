# Standard library imports
import os
import PySimpleGUI as sg
from PIL import Image

# Function to validate file type
def is_valid_file_type(file_path):
    valid_extensions = ('.gif', '.jpg', '.png', '.pcx', '.bmp')
    return file_path.lower().endswith(valid_extensions)

# Function to handle file loading
def handle_file_load(file_path, file_list, window, image_open, clear_color_pallete):
    if os.path.exists(file_path):
        file_list.append(file_path)
        window["-FILE LIST-"].update(file_list)
        full_image, color_palette, image_dimensions = image_open(file_path)
        clear_color_pallete(file_path)
        return file_path, full_image, color_palette, image_dimensions
    return None, None, None, None

# Function to display error popup
def show_error_popup(message, font):
    sg.Popup(message, font=font, button_type=5, title="Error!")

# Function to convert an image to RGB
def convert_to_RGB(current_image, output_path="tmp.png"):
    file_name = os.path.basename(current_image)
    if file_name.split(".")[1] == "png":
        png = Image.open(current_image).convert('RGBA')
        png.load()
        background = Image.new("RGB", png.size, (255, 255, 255))
        background.paste(png, mask=png.split()[3])
        background.save(output_path, 'PNG')
    elif file_name.split(".")[1] != "pcx":
        image = Image.open(current_image)
        RGB_image = image.convert("RGB")
        RGB_image.save(output_path)
