# Program Description: Desktop Application that opens, reads, and transforms image files
# Author: John Cedric R. Warain, 4 - BSCS

# Standard library imports
import io
import os
from os.path import exists
import struct
import math

# Third-party imports
import cv2
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk  # Image for open, ImageTk for display
import numpy as np

# Local application imports
from spatial_filtering_window import open_window
from LSB_watermarking_window import open_bit_plane_window
from helpers import is_valid_file_type, handle_file_load, show_error_popup, convert_to_RGB
from ui.image_display import ImageDisplayManager
from ui.layout import create_layout
from ui.config import UI_THEME, UI_FONT
from ui.controls import UIControls

sg.theme(UI_THEME)

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

    # function to show the update the slider
    def clear_info():           # clear and hide widgets whenever another image has been viewed
        window["-transformation-"].update('')  
        window["-TRANSFORMATION-"].update('')     
        window["-histogram-"].update('')   
        window["-HISTOGRAM-"].update('')  
        window["-slider-"].update(visible=False) 
        window["threshold_value"].update(visible=False) 
        window["Apply"].update(visible=False)
        window["threshold"].update(visible=False)     
        window["left"].update(visible=False)  
        window["right"].update(visible=False)    
    
    # function to clear the colour palette image
    def clear_color_pallete(current_image):     # clear color palette if current image is not in pcx format
        file_name = os.path.basename(current_image)  
        if(file_name.split(".")[1] != "pcx"):
            window["-colorpalette-"].update('') 

    # function to open an image and the header information
    def image_open(file):   # function for opening an image

        file_name = os.path.basename(file)  # get the image's filename only
        if(file_name.split(".")[1] != "pcx"):    # check if image is not in PCX format
            image = Image.open(file)    # open the file
            image.thumbnail((256, 256))     # resize the image
            bio = io.BytesIO()  # convert image into a byte stream
            image.save(bio, "PNG")      # save the image as PNG
            window["-IMAGE-"].update(data = bio.getvalue())     # show the image
            get_headers_info(file)
            return None, None, None
            
        else:   # get pcx image data [15]
            
            with open(file, 'rb') as f:     # read the image as binary
                byte_data = []
                while (byte := f.read(1)):      # read all the bytes in the image
                    byte_data.append(int(struct.unpack('B', byte)[0]))
    
                ColorPalette = []           #list representing the color palette
                if (len(byte_data) > 768):          #  color palette is found 768 bytes from the end of the file
                    for i in range(int(len(byte_data)) - 768, int(len(byte_data)), 3):     # the palette is stored as a sequence of RGB triples
                        temp_array = []
                        temp_array.append([byte_data[i], byte_data[i + 1], byte_data[i + 2]])       # group the RGB triples together to represent the color palette
                        ColorPalette.extend(temp_array)

                # PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
                color_palette = Image.new('RGB', (64, 64), "black") # create a completely black 64x64 image for the color palette
                pixels = color_palette.load()   # create the pixel map

                k = 0
                for i in range(0, color_palette.size[0], 4):    # for every column (color_palette.size[0] gets the width)
                    for j in range(0, color_palette.size[1], 4):    # for every row (color_palette.size[1] gets the height)
                        for x in range(4):              # 4x4 boxes will represent a colour
                            for y in range(4):
                                pixels[i + x, j + y] = (ColorPalette[k][0], ColorPalette[k][1], ColorPalette[k][2]) # set the colour accordingly for the pixel located in each column and row in the pixel map
                        k = k + 1  

                color_palette.save("color_palette.png")
                window["-colorpalette-"].update("color_palette.png")     # save and show the color palette

                imageData = Image.new('RGB', (256, 256), "black")   # create a completely black 256x256 image for printing the actual image
                pixels = imageData.load()   # load the pixel map
                
                imageColorValues = [[0 for x in range(3)] for y in range(256 * 256)]    # the resulting image will have a height, width, and channel depth of 256, 256, and 3, respectively
                paletteIndex = []
                position = 128
                runlength = 0
                runvalue = 0

                full_image = np.zeros([256, 256, 3])
                while (position < int(len(byte_data) - 768) ):  # this range represents where the image data is located ( 128 bytes < position < (byte_data - 768))
                    Byte = byte_data[position]   
                    position = position + 1

                    if ((Byte & 0xC0) == 0xC0 and position < (len(byte_data) - 768)):  # RLE pair representing a series of several pixels of a single value
                        runlength = (Byte & 0x3F)            # run length have a value range of 0-63, and its length can be extracted through bitwise addition 
                        runvalue = int(byte_data[position])          # run value represents the given palette index for the pixels
                        position = position + 1

                    else:   # any other case, the byte is interpreted as a single pixel value of a given palette index or color value
                        runlength = 1
                        runvalue = Byte 
                    
                    for j in range(0, runlength):
                        paletteIndex.append(runvalue)
                
                for i in range(0, 256 * 256):
                    imageColorValues[i] = ColorPalette[paletteIndex[i]] # get the color from the color palette
                    y = int(i / 256)                # get the x and y coordinate for the pixel  
                    x = int(i - (256 * y))
                    pixels[x, y] = (imageColorValues[i][0], imageColorValues[i][1], imageColorValues[i][2]) # set the  color of the pixel in the appropriate pixel map
                    full_image[y][x] = (imageColorValues[i][0], imageColorValues[i][1], imageColorValues[i][2])
                
                full_image = np.array(full_image)
                image_dimensions = np.array(full_image)
                full_image = full_image.reshape(full_image.shape[0] * full_image.shape[1], 3)

                new_array = [tuple(row) for row in full_image]
                colorpalette, counter = np.unique(new_array, axis=0, return_counts=True)

                color_palette = np.uint8(np.array([val for (_, val) in sorted(zip(counter, colorpalette), key=lambda x: x[0], reverse=True)])) # sort color palette- 
                                                                                                                                    # based on most frequently used
                imageData.save("tmp.png")
                window["-IMAGE-"].update("tmp.png")     # save and show the image

            f.close()
            get_headers_info(file)
            return full_image, color_palette, image_dimensions 

    # function to get the header information
    def get_headers_info(file):   # get pcx image header data [15]

        headers_list = [    
            "-manufacturer-", 
            "-version-", 
            "-encoding-", 
            "-bitsperpixel-", 
            "-dimensions-", 
            "-hdpi-", 
            "-vdpi-", 
            "-colorplanes-", 
            "-bytesperline-", 
            "-paletteinformation-", 
            "-hss-", 
            "-vss-"
        ]

        headers_name = [    #    header information
            "Manufacturer: Zshoft .pcx ",
            "Version: ",
            "Encoding: ",
            "Bits per Pixel: ",
            "Image Dimensions: ",
            "HDPI: ",
            "VDPI: ",
            "Number of Color Planes: ",
            "Bytes Per Line: ",
            "Palette Information: ",
            "Horizontal Screen Size: ",
            "Vertical Screen Size: "
        ]

        file_name = os.path.basename(file)  # get the image's filename only
        if(file_name.split(".")[1] != "pcx"):    # check if image is not in PCX format 
            window["-headerinfo-"].update("")      # if it isn't a PCX image, don't display its header information
            for i in range(len(headers_list)):
                window[headers_list[i]].update("")   
        else:       # only pcx file
            with open(f''+file, 'rb') as pcx:     # read PCX header, and identify the information represented in the bytes
                headers_info_list_1 = [
                    str(struct.unpack('B', pcx.read(1))[0]),
                    str(struct.unpack('B', pcx.read(1))[0]),
                    str(struct.unpack('B', pcx.read(1))[0]),
                    str(struct.unpack('B', pcx.read(1))[0]),
                    str(struct.unpack('H', pcx.read(2))[0]) + " " 
                    + str(struct.unpack('H', pcx.read(2))[0]) + " " 
                    + str(struct.unpack('H', pcx.read(2))[0]) + " " 
                    + str(struct.unpack('H', pcx.read(2))[0]),
                    str(struct.unpack('H', pcx.read(2))[0]),
                    str(struct.unpack('H', pcx.read(2))[0]),
                ]
                pcx.seek(65)    # offset by 65 bytes to skip irrelevant information
                header_info_list_2 = [
                    str(struct.unpack('B', pcx.read(1))[0]),
                    str(struct.unpack('H', pcx.read(2))[0]),
                    str(struct.unpack('H', pcx.read(2))[0]),
                    str(struct.unpack('H', pcx.read(2))[0]),
                    str(struct.unpack('H', pcx.read(2))[0]),
                ]

                headers_info_list = headers_info_list_1 + header_info_list_2

                window["-headerinfo-"].update("PCX Header Information:") 
                window[headers_list[0]].update(headers_name[0] + "(" + headers_info_list[0] + ")")   

                for i in range(1, len(headers_list)):       # show the information
                     window[headers_list[i]].update(headers_name[i] + headers_info_list[i])   

    # function to delete the image files 
    def delete_file(file_name):     # delete the generated images
        file_exists = exists(file_name)
        if file_exists:  
            os.remove(file_name)
  
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
                
        elif event == "-FILE LIST-":    # call image_open() whenever the the user clicks on the list box element
            try:
                clear_info()     
                file_list_name = values["-FILE LIST-"][0]     
                full_image, color_palette, image_dimensions = image_open(file_list_name)
                state.current_image_path = file_list_name
                clear_color_pallete(state.current_image_path)
            except:
                pass

        elif event == "Load Image":  # "Load Image" event
            clear_info()
            file_exist = values['-FILE-']
            if not file_exist:
                pass
            elif not is_valid_file_type(file_exist):
                show_error_popup("Please choose an image file.", UI_FONT)
            else:
                state.current_image_path, full_image, color_palette, image_dimensions = handle_file_load(
                    file_path, file_list, window, image_open, clear_color_pallete
                )
            
        elif event == "R":    # show red channel [16]
            if state.current_image_path == "":         
                pass
            else:
                clear_info()
                clear_color_pallete(state.current_image_path)
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
                clear_info()
                clear_color_pallete(state.current_image_path)
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
                clear_info()
                clear_color_pallete(state.current_image_path)
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
                clear_info()
                clear_color_pallete(state.current_image_path)
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
                clear_info()
                clear_color_pallete(state.current_image_path)
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
                clear_info()
                clear_color_pallete(state.current_image_path)
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

                clear_info()
                clear_color_pallete(state.current_image_path)
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

                clear_info() 
                clear_color_pallete(state.current_image_path)
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
