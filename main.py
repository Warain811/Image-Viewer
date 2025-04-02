# Program Description: Desktop Application that opens, reads, and transforms image files
# Author: John Cedric R. Warain, 4 - BSCS

# Standard library imports
import io
import os
from os.path import exists
import math

# Third-party imports
import cv2
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import numpy as np

# Local application imports
from src.features.spatial_filtering import open_window
from src.features.watermarking import open_bit_plane_window
from src.core.utils import is_valid_file_type, handle_file_load, show_error_popup, convert_to_RGB, delete_file
from ui.image_display import ImageDisplayManager
from ui.layout import create_layout
from ui.config import UI_THEME, UI_FONT
from ui.controls import UIControls
from src.core.color_palette import clear_color_palette
from src.core.image_loader import image_open

class ImageViewerState:
    def __init__(self):
        self.transformation_mode = None  # Replaces 'flag'
        self.current_image_path = ""    # Replaces 'current_image'

def main(file_list):
    layout = create_layout()
    window = sg.Window("Image Viewer", layout, font=UI_FONT, resizable=True, finalize=True)
    
    # Initialize managers
    display_manager = ImageDisplayManager(window)
    ui_controls = UIControls(window)
    state = ImageViewerState()
    sg.theme(UI_THEME)

    window["-slider-"].update(visible=False)    # these values are initially invisible
    window["Apply"].update(visible=False)
    window["threshold_value"].update(visible=False)
    window["threshold"].update(visible=False) 
    window["left"].update(visible=False)  
    window["right"].update(visible=False)   

    while True:     # event loop
        event, values = window.read()   # this is for displaying and interacting with the window

        if event == "Exit" or event == sg.WIN_CLOSED:   # this is to exit the program
            break

        window['threshold_value'].update(values['-slider-'])

        def handle_transformation(func):
            """Helper to handle common image transformation flow"""
            if not state.current_image_path:
                return
                
            ui_controls.clear_info()
            clear_color_palette(window, state.current_image_path)
            convert_to_RGB(state.current_image_path)
            func()

        if event == "Browse":       
            file_path = sg.popup_get_file(
                file_types=[
                    ("PCX (*.pcx)", "*.pcx"),
                    ("JPEG (*.jpg)", "*.jpg"), 
                    ("PNG (*.png)", "*.png"),
                    ("GIF (*.gif)", "*.gif"),
                    ("All files (*.*)", "*.*")
                ],
                no_window=True,
                message=""
            )
            
            if file_path:  # Only update if a file was selected
                window['-FILE-'].update(os.path.basename(file_path))

        elif event == "right":
            increment = round(values["-slider-"], 1)
            if state.transformation_mode == 1:
                ui_controls.update_slider(increment + 1)
            elif state.transformation_mode == 2:
                ui_controls.update_slider(increment + 0.1)

        elif event == "left":
            decrement = round(values["-slider-"], 1)
            if decrement != 0:
                if state.transformation_mode == 1:
                    ui_controls.update_slider(decrement - 1)
                elif state.transformation_mode == 2:
                    ui_controls.update_slider(decrement - 0.1)
                
        elif event == "-FILE LIST-":    
            try:
                ui_controls.clear_info()     
                file_list_name = values["-FILE LIST-"][0]     
                full_image, color_palette, image_dimensions = image_open(file_list_name, window)
                state.current_image_path = file_list_name
                clear_color_palette(window, state.current_image_path)
            except:
                pass

        elif event == "Load Image":
            ui_controls.clear_info()
            file_exist = values['-FILE-']
            if not file_exist:
                pass
            elif not is_valid_file_type(file_exist):
                show_error_popup("Please choose an image file.", UI_FONT)
            else:
                state.current_image_path, full_image, color_palette, image_dimensions = handle_file_load(
                    file_path, file_list, window, lambda f: image_open(f, window), lambda path: clear_color_palette(window, path)
                )

        elif event == "R":    # show red channel [16]
            def process_red():
                image = cv2.imread("tmp.png")
                r = image.copy()
                r[:,:,0] = r[:,:,1] = 0  # extract red channel
                cv2.imwrite("transformation.png", r)
                display_manager.display_transformation("-transformation-", "-TRANSFORMATION-", "Red Channel:")
                display_manager.display_histogram(r)
            
            handle_transformation(process_red)
                
        elif event == "G":      # show the green channel [16]
            def process_green():
                image = cv2.imread("tmp.png")
                g = image.copy()
                g[:,:,0] = g[:,:,2] = 0  # extract green channel
                cv2.imwrite("transformation.png", g)
                display_manager.display_transformation("-transformation-", "-TRANSFORMATION-", "Green Channel:")
                display_manager.display_histogram(g)
            
            handle_transformation(process_green)

        elif event == "B":       # show the blue channel [16]
            def process_blue():
                image = cv2.imread("tmp.png")
                b = image.copy()
                b[:,:,1] = b[:,:,2] = 0  # extract blue channel
                cv2.imwrite("transformation.png", b)
                display_manager.display_transformation("-transformation-", "-TRANSFORMATION-", "Blue Channel:")
                display_manager.display_histogram(b)
            
            handle_transformation(process_blue)

        elif event == "grayscale":       # apply grayscale transformation [5]
            def process_grayscale():
                image = cv2.imread("tmp.png")
                grayscale = image.copy()
                r, g, b = grayscale[:,:,2], grayscale[:,:,1], grayscale[:,:,0]
                gray = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)
                cv2.imwrite("transformation.png", gray)
                display_manager.display_transformation("-transformation-", "-TRANSFORMATION-", "Grayscale Transformation:")
            
            handle_transformation(process_grayscale)
    
        elif event == "negative":       # apply negative transformation [6]
            def process_negative():
                image = cv2.imread("tmp.png")
                negative = abs(255 - image[:,:,:])
                cv2.imwrite("transformation.png", negative)
                display_manager.display_transformation("-transformation-", "-TRANSFORMATION-", "Negative Transformation:")
            
            handle_transformation(process_negative)
        
        elif event == "negative_grayscale":       # apply negative transformation of grayscale image [6]
            def process_negative_grayscale():
                image = cv2.imread("tmp.png")
                r, g, b = image[:,:,2], image[:,:,1], image[:,:,0]
                gray = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)
                neg_gray = abs(255 - gray[:,:])
                cv2.imwrite("transformation.png", neg_gray)
                display_manager.display_transformation("-transformation-", "-TRANSFORMATION-", "Negative Transformation:")
            
            handle_transformation(process_negative_grayscale)
        
        elif event == "b_and_w":       # apply black and white transformation
            def process_black_and_white():
                ui_controls.show_slider(255)
                png = Image.open(state.current_image_path).convert('RGBA')
                background = Image.new("RGB", png.size, (255, 255, 255))
                background.save('transformation.png', 'PNG')
                display_manager.display_transformation("-transformation-", "-TRANSFORMATION-", "Black and White Transformation:")
                window["threshold"].update("B&W Threshold Value:")
                state.transformation_mode = 1
            
            handle_transformation(process_black_and_white)
                
        elif event == "gamma":       # apply gamma transformation 
            def process_gamma():
                ui_controls.show_slider(20)
                image = cv2.imread("tmp.png")
                cv2.imwrite("transformation.png", image)
                display_manager.display_transformation("-transformation-", "-TRANSFORMATION-", "Gamma Transformation:")
                window["threshold"].update("Gamma Threshold Value:")
                state.transformation_mode = 2
            
            handle_transformation(process_gamma)

        elif event == "Apply":       # apply black and white, or gamma transformation
            if state.transformation_mode == 1:
                slider = int(math.floor(float(values["threshold_value"])))
                image = cv2.imread("tmp.png")
                r, g, b = image[:,:,2], image[:,:,1], image[:,:,0]
                gray = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)
                rows, cols = gray.shape
                for x in range(rows):
                    for y in range(cols):
                        gray[x][y] = 255 if gray[x][y] >= slider else 0
                cv2.imwrite("transformation.png", gray)
                display_manager.display_transformation("-transformation-", "-TRANSFORMATION-", "Black and White Transformation:")
                
            elif state.transformation_mode == 2:
                slider = float(values["threshold_value"])
                image = cv2.imread("tmp.png")
                gamma_transform = (255*(np.power((image/255), (slider/4)))).clip(0, 255).astype(np.uint8)
                cv2.imwrite("transformation.png", gamma_transform)
                display_manager.display_transformation("-transformation-", "-TRANSFORMATION-", "Gamma Transformation:")
            
        elif event == "spatial_filtering":       # apply spatial filtering
            def process_spatial_filtering():
                image = cv2.imread("tmp.png")
                r, g, b = image[:,:,2], image[:,:,1], image[:,:,0]
                grayscale = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)
                cv2.imwrite("transformation.png", grayscale)
                file_name = os.path.basename(state.current_image_path)
                open_window(file_name, grayscale, full_image, color_palette, image_dimensions)
            
            handle_transformation(process_spatial_filtering)
        
        elif event == "bit_plane":
            def process_bit_plane():
                image = cv2.imread("tmp.png")
                r, g, b = image[:,:,2], image[:,:,1], image[:,:,0]
                grayscale = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)
                cv2.imwrite("transformation.png", grayscale)
                open_bit_plane_window(state.current_image_path, grayscale)
            
            handle_transformation(process_bit_plane)

    delete_file("tmp.png")
    delete_file("transformation.png")
    delete_file("color_palette.png")
    delete_file("decompressed.png")
    delete_file("bit_plane_slice.png")
    delete_file("watermark_image.png")
    delete_file("watermark.png")

    window.close()    # this closes the window

if __name__ == "__main__":  # declare an empty file_list for the listbox element, 
                            # before we call the main function
    file_list = []
    main(file_list)
