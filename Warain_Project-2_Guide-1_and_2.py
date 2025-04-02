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
from spatial_filtering_window import open_window
from LSB_watermarking_window import open_bit_plane_window
from helpers import is_valid_file_type, handle_file_load, show_error_popup, convert_to_RGB, delete_file
from ui.image_display import ImageDisplayManager
from ui.layout import create_layout
from ui.config import UI_THEME, UI_FONT
from ui.controls import UIControls
from color_palette import clear_color_palette
from image_loader import image_open

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

        if event == "Browse":       # this lets the user choose the image from a directory
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
            
            # Only update if a file was actually selected
            if file_path:  # Check if file_path is not None
                window['-FILE-'].update(os.path.basename(file_path))

        elif event == "right":  # update the slider value 
            if(state.transformation_mode == 1):
                increment = round(values["-slider-"], 1)
                ui_controls.update_slider(increment + 1)
            elif(state.transformation_mode == 2):
                increment = round(values["-slider-"], 1)
                ui_controls.update_slider(increment + 0.1)

        elif event == "left":
            if(state.transformation_mode == 1):
                decrement = round(values["-slider-"], 1)
                if (decrement != 0):
                    ui_controls.update_slider(decrement - 1)
            elif(state.transformation_mode == 2):
                decrement = round(values["-slider-"], 1)
                if (decrement != 0):
                    ui_controls.update_slider(decrement - 0.1)
                
        elif event == "-FILE LIST-":    # call image_open() whenever the user clicks on the list box element
            try:
                ui_controls.clear_info()     
                file_list_name = values["-FILE LIST-"][0]     
                full_image, color_palette, image_dimensions = image_open(file_list_name, window)
                state.current_image_path = file_list_name
                clear_color_palette(window, state.current_image_path)
            except:
                pass

        elif event == "Load Image":  # "Load Image" event
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
            if state.current_image_path == "":         
                pass
            else:
                ui_controls.clear_info()
                clear_color_palette(window, state.current_image_path)
                convert_to_RGB(state.current_image_path)

                image = cv2.imread("tmp.png")   # cv2.imread() returns a BGR (Blue-Green-Red) array
                r = image.copy()
                r[:,:,0] = r[:,:,1] = 0     # extract the red channel of the image 
                cv2.imwrite("transformation.png", r)

                display_manager.display_transformation(
                    "-transformation-", 
                    "-TRANSFORMATION-", 
                    "Red Channel:"
                )
                display_manager.display_histogram(r)
                
        elif event == "G":      # show the green channel [16]
            if state.current_image_path == "":
                pass
            else:
                ui_controls.clear_info()
                clear_color_palette(window, state.current_image_path)
                convert_to_RGB(state.current_image_path)

                image = cv2.imread("tmp.png")   # cv2.imread() returns a BGR (Blue-Green-Red) array
                g = image.copy()
                g[:,:,0] = g[:,:,2] = 0     # extract the green channel of the image
                cv2.imwrite("transformation.png", g)

                display_manager.display_transformation(
                    "-transformation-", 
                    "-TRANSFORMATION-", 
                    "Green Channel:"
                )
                display_manager.display_histogram(g)     

        elif event == "B":       # show the blue channel [16]
            if state.current_image_path == "":
                pass
            else:
                ui_controls.clear_info()
                clear_color_palette(window, state.current_image_path)
                convert_to_RGB(state.current_image_path)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                b = image.copy()
                b[:,:,1] = b[:,:,2] = 0     # extract the blue channel of the image
                cv2.imwrite("transformation.png", b)

                display_manager.display_transformation(
                    "-transformation-", 
                    "-TRANSFORMATION-", 
                    "Blue Channel:"
                )
                display_manager.display_histogram(b)

        elif event == "grayscale":       # apply grayscale transformation [5]
            if state.current_image_path == "":
                pass
            else:
                ui_controls.clear_info()
                clear_color_palette(window, state.current_image_path)
                convert_to_RGB(state.current_image_path)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                grayscale = image.copy()
                r, g, b = grayscale[:,:,2], grayscale[:,:,1], grayscale[:,:,0]  # get the values of each color channel 
                gray = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)     #  apply different set of weights for our channel averaging (weights taken from ITU-R 601-2 luma transform)                                                                        
                cv2.imwrite("transformation.png", gray)
               
                display_manager.display_transformation(
                    "-transformation-", 
                    "-TRANSFORMATION-", 
                    "Grayscale Transformation:"
                )
    
        elif event == "negative":       # apply negative transformation [6]
            if state.current_image_path == "":
                pass
            else:
                ui_controls.clear_info()
                clear_color_palette(window, state.current_image_path)
                convert_to_RGB(state.current_image_path)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                negative = image.copy()
                negative = abs(255 - negative[:,:,:])   # subtract 255 by the value of each pixel in each color channels
                cv2.imwrite("transformation.png", negative)

                display_manager.display_transformation(
                    "-transformation-", 
                    "-TRANSFORMATION-", 
                    "Negative Transformation:"
                )
        
        elif event == "negative_grayscale":       # apply negative transformation of grayscale image [6]
            if state.current_image_path == "":
                pass
            else:
                ui_controls.clear_info()
                clear_color_palette(window, state.current_image_path)
                convert_to_RGB(state.current_image_path)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                negative_grayscale = image.copy()
                r, g, b = negative_grayscale[:,:,2], negative_grayscale[:,:,1], negative_grayscale[:,:,0]  # get the red, green, and blue channels
                gray = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)     #  ITU-R 601-2 luma transform
                neg_gray = abs(255 - gray[:,:])     # subtract by 255 the value of each pixel in the grayscale image
                cv2.imwrite("transformation.png", neg_gray)

                display_manager.display_transformation(
                    "-transformation-", 
                    "-TRANSFORMATION-", 
                    "Negative Transformation:"
                )
        
        elif event == "b_and_w":       # apply black and white transformation
            if state.current_image_path == "":
                pass
            else:

                ui_controls.clear_info()
                clear_color_palette(window, state.current_image_path)
                ui_controls.show_slider(255)

                png = Image.open(state.current_image_path).convert('RGBA')  # convert the image into RGBA
                background = Image.new("RGB", png.size, (255, 255, 255)) # create a white, blank image with the same dimensions as the input image 
                background.save('transformation.png', 'PNG')       # save the converted into a png file

                display_manager.display_transformation(
                    "-transformation-", 
                    "-TRANSFORMATION-", 
                    "Black and White Transformation:"
                )
                window["threshold"].update("B&W Threshold Value:")  

                state.transformation_mode = 1
                
        elif event == "gamma":       # apply gamma transformation 
            if state.current_image_path == "":
                pass
            else:

                ui_controls.clear_info() 
                clear_color_palette(window, state.current_image_path)
                ui_controls.show_slider(20)        

                convert_to_RGB(state.current_image_path)
                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                cv2.imwrite("transformation.png", image)     

                display_manager.display_transformation(
                    "-transformation-", 
                    "-TRANSFORMATION-", 
                    "Gamma Transformation:"
                )
                window["threshold"].update("Gamma Threshold Value:")

                state.transformation_mode = 2

        elif event == "Apply":       # apply black and white, or gamma transformation

            if (state.transformation_mode == 1):     # check if user clicked on button (with key "b_and_w")
                slider = int(math.floor(float(values["threshold_value"])))
              
                convert_to_RGB(state.current_image_path)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                negative_grayscale = image.copy()
                r, g, b = negative_grayscale[:,:,2], negative_grayscale[:,:,1], negative_grayscale[:,:,0] 
                gray = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)     #  get grayscale image through ITU-R 601-2 luma transform

                rows, cols = gray.shape     # get the dimensions of the image
                for x in range(rows):
                    for y in range(cols):
                        if(gray[x][y] >= slider):   # compare grayscale value of the pixels to threshold 
                            gray[x][y] =  255       # if above or equal to the threshold, turn the pixel white
                        else:
                            gray[x][y] =  0         # if below threshold, turn the pixel black
                
                cv2.imwrite("transformation.png", gray)
                display_manager.display_transformation(
                    "-transformation-", 
                    "-TRANSFORMATION-", 
                    "Black and White Transformation:"
                )
                
            elif (state.transformation_mode == 2):    # check if user clicked on button (with key "gamma") [7] [8]
                slider = float(values["threshold_value"]) 
                
                convert_to_RGB(state.current_image_path)

                image = cv2.imread("tmp.png")   #   imread() returns a BGR (Blue-Green-Red) array
                gamma_transform = image.copy()
                gamma_transform = (255*(np.power((gamma_transform/255), (slider/4)))).clip(0, 255).astype(np.uint8) # s = cr^(γ/4), where c=1, r=[0,255], and γ is any value from 0-20
                                                                                                                    # s = 255*(c(r/255)^(γ/4))
                cv2.imwrite("transformation.png", gamma_transform)
                display_manager.display_transformation(
                    "-transformation-", 
                    "-TRANSFORMATION-", 
                    "Gamma Transformation:"
                )
            
        elif event == "spatial_filtering":       # apply black and white, or gamma transformation
            
            if state.current_image_path == "":
                pass
            else:
                convert_to_RGB(state.current_image_path)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                grayscale = image.copy()
                r, g, b = grayscale[:,:,2], grayscale[:,:,1], grayscale[:,:,0]  # get the values of each color channel 
                grayscale = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)     #  ITU-R 601-2 luma transform
                cv2.imwrite("transformation.png", grayscale)

                file_name = os.path.basename(state.current_image_path)  # get the image's filename only
                open_window(file_name, grayscale, full_image, color_palette, image_dimensions)
        
        elif event == "bit_plane":

            if state.current_image_path == "":
                pass
            else:
                convert_to_RGB(state.current_image_path)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                grayscale = image.copy()
                r, g, b = grayscale[:,:,2], grayscale[:,:,1], grayscale[:,:,0]  # get the values of each color channel 
                grayscale = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)     #  ITU-R 601-2 luma transform
                cv2.imwrite("transformation.png", grayscale)

                open_bit_plane_window(state.current_image_path, grayscale)

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
