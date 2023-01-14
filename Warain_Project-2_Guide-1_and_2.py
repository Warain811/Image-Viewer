# Program Description: Desktop Application that opens, reads, and transforms image files
# Author: John Cedric R. Warain, 4 - BSCS

from re import L
from tkinter import Y
import cv2      # import modules
import io  
import os
from os.path import exists
import PySimpleGUI as sg
import struct 
import matplotlib.pyplot as plt   
from PIL import Image, ImageTk  #Image for open, ImageTk for display
import numpy as np
import math
from spatial_filtering_window import open_window
from LSB_watermarking_window import open_bit_plane_window

def main(file_list): 
    
    flag = 0
    current_image = ""
    # function to convert any image file into a png
    def convert_to_RGB(current_image):
        file_name = os.path.basename(current_image)  # get the image's filename only
        
        if(file_name.split(".")[1] == "png"):    # check if image is in PNG format [1] [2]
            png = Image.open(current_image).convert('RGBA')  # convert the image into RGBA
            png.load()               # required for png.split()
            background = Image.new("RGB", png.size, (255, 255, 255)) # if the image has a transparent background, turn the background white
            background.paste(png, mask=png.split()[3])      # 3 is the alpha channel
            background.save('tmp.png', 'PNG')       # save the converted into a png file 

        elif(file_name.split(".")[1] != "pcx"):     # every other image format besides .png and .pcx
            image = Image.open(current_image)       # open the image
            RGB_image = image.convert("RGB")        # convert the image into RGB
            RGB_image.save("tmp.png")           # save the converted into a png file

    # function to display the image
    def transformation(transform_name, transform_image, transformation):
        image = Image.open("transformation.png")     # open the transformed image [1]
        image.thumbnail((256, 256))     # resize the image
        window[transform_name].update(transformation)   
        window[transform_image].update(data = ImageTk.PhotoImage(image))    # display the image's respective transformation

    # function to get the histogram of an image
    def histogram(image):    # calculate the histogram [3] [4]
        plt.ticklabel_format(style='plain')
        vals = image.sum(axis = 2).flatten()    # flatten the channel into a 1D array
        counts, bins = np.histogram(vals, range(257))   #   calculate the histogram 
        plt.bar(bins[:-1] - 0.5, counts, width=1, edgecolor='none')     # plot histogram centered on values 0 to 255
        plt.xlim([-2, 255.5])
        plt.savefig('histogram.png', bbox_inches='tight', dpi=60)   # save the histogram as an image
        plt.close()

        window["-histogram-"].update("Histogram:")   
        window["-HISTOGRAM-"].update("histogram.png")     # display the histogram

        os.remove("histogram.png")      # delete the generated image

    # function to show the slider widget
    def show_slider(slider_value):
        window["left"].update(visible=True)         # turn certain widgets visible for transformation
        window["right"].update(visible=True) 
        window["-slider-"].update(visible=True, range = (0, slider_value))   
        window["Apply"].update(visible=True)
        window["threshold"].update(visible=True) 
        window["threshold_value"].update(visible=True) 

    # function to show the update the slider
    def update_slider(value):
        window['-slider-'].update(round(value, 1))
        window['threshold_value'].update(round(value, 1))
    
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

    sg.theme('DarkGrey8')   # theme of the program
    font = ("04b03", 12)     # font style of the program

    file_column = [     # left column of the program
        [
            sg.Text("File Name:", text_color = "yellow"),       # text element
            sg.Input(size=(26, 1), disabled = True, text_color = "black", key="-FILE-"),    # input element with key 'FILE'
            sg.Button('Browse'),        # 'browse' button element
            sg.Button("Load Image"),    # 'load image' button element 
        ],

        [
            sg.Text("Load History:", size = (60, 1), text_color = "yellow", justification='center')   # text element  
        ],
    
        [
            sg.Listbox      # listbox element that shows the list of images that were previously loaded
            (
                values=[], 
                enable_events=True, 
                size=(55, 7), 
                key="-FILE LIST-", 
                horizontal_scroll=True
            ),
        ],

        [sg.Text("Transformation Options:", size = (60, 1), text_color = "yellow", justification='center'), ], # text element
        
        [
            sg.Button('R', image_filename ='red.png', pad = ((5, 0), (0, 0)), border_width = 1, tooltip=" Show Red Channel and its Histogram "),     # button elements that deal with transforming the image
            sg.Button('G', image_filename ='green.png', pad = ((10, 0), (0, 0)), border_width = 1, tooltip="Show Green Channel and its Histogram "),        
            sg.Button('B', image_filename ='blue.png', pad = ((10, 0), (0, 0)), border_width = 1, tooltip="Show Blue Channel and its Histogram "),       
            sg.Button('G', key = 'grayscale', image_filename ='grayscale.png', pad = ((10, 0), (0, 0)), border_width = 1, tooltip=" Apply Grayscale Transformation " ),        
            sg.Button(key = 'negative_grayscale', image_filename ='negative_grayscale.png', pad = ((10, 0), (0, 0)), border_width = 1, tooltip=" Apply Negative Transformation to Grayscale Image  " ),        
            sg.Button(key = 'negative', image_filename ='negative.png', pad = ((10, 0), (0, 0)), border_width = 1, tooltip=" Apply Negative Transformation " ),        
            sg.Button(key = 'b_and_w', image_filename ='b_and_w.png', pad = ((10, 0), (0, 0)), border_width = 1, tooltip=" Apply Black and White Transformation Via Manual Thresholding " ),        
            sg.Button(key = 'gamma', image_filename ='gamma.png', pad = ((10, 0), (0, 0)), border_width = 1, tooltip=" Apply Power Law (Gamma) Transformation " ),
            sg.Button(key = 'bit_plane', image_filename ='bit_plane.png', pad = ((10, 0), (0, 0)), border_width = 1, tooltip=" Apply Watermarking through Bit Planes " ),         
        ],
        
        [sg.Button('Spatial Filtering', key = 'spatial_filtering', image_filename ='spatial_filtering.png', pad = ((5, 0), (15, 0)), border_width = 1, tooltip=" Apply Spatial Filtering ")],     # button element for spatial filtering
             
    ]

    image_viewer_column = [     # right column of the program

        [sg.Text("View of the image:", text_color = "yellow", justification = 'center')],     # text elements
        [
            sg.Image(key="-IMAGE-", size = (320, 240), filename="empty.png"),   # image elements
            sg.Image(key="-colorpalette-", size = (90, 90)),                  
        ], 
        [sg.Text("")],      
        [sg.Text(size=(30, 1), key="-headerinfo-", text_color = "yellow", justification = 'center')],   # these text elements-
        [sg.Text(size=(30, 1), key="-manufacturer-", justification = 'center')],                        # represent the PCX header information
        [sg.Text(size=(30, 1), key="-version-", justification = 'center')], 
        [sg.Text(size=(30, 1), key="-encoding-", justification = 'center')],
        [sg.Text(size=(30, 1), key="-bitsperpixel-", justification = 'center')],
        [sg.Text(size=(40, 1), key="-dimensions-", justification = 'center')],
        [sg.Text(size=(30, 1), key="-hdpi-", justification = 'center')],
        [sg.Text(size=(30, 1), key="-vdpi-", justification = 'center')],
        [sg.Text(size=(30, 1), key="-colorplanes-", justification = 'center')],
        [sg.Text(size=(30, 1), key="-bytesperline-", justification = 'center')],
        [sg.Text(size=(30, 1), key="-paletteinformation-", justification = 'center')],
        [sg.Text(size=(30, 1), key="-hss-", justification = 'center')],
        [sg.Text(size=(30, 1), key="-vss-", justification = 'center')],    
    ]

    transformation_column = [
        [sg.Text(size=(45, 1), key="-transformation-", text_color = "yellow", justification = 'center')],   # elements from 217-229  
        [sg.Image(key="-TRANSFORMATION-", size = (320, 240))],                                              # are for image transforming
        [
            sg.Input(size=(5, 1), text_color = "black", key="threshold_value", disabled=True),  
            sg.Text("", key = "threshold", text_color = "yellow"),
        ],    

        [
            sg.Slider(range = (0, 255), key='-slider-', orientation='h', enable_events=True, disable_number_display= True, resolution = False),
            sg.Button(key='left', image_filename = "left_arrow.png", pad = ((2, 0), (3, 0))),
            sg.Button(key='right', image_filename = "right_arrow.png", pad = ((3, 0), (3, 0))),
            sg.Button('Apply', key='Apply', pad = ((10, 0), (10, 0))),        
        ],

        [sg.Text(size=(30, 1), key="-histogram-", text_color = "yellow", justification = 'center')],   # text element
        [sg.Image(key="-HISTOGRAM-")], # image element for the histogram
    ]
    
    layout = [      # this defines the window's contents
        [
            sg.Column(file_column, vertical_alignment='center', p = ((0, 3), (60, 75))),    # column element
            sg.VSeperator(),       # this is a vertical line that shows the separation of the columns
            sg.Column(image_viewer_column, element_justification = "center", expand_y= True),   # column element
            sg.VSeperator(),       # this is a vertical line that shows the separation of the columns
            sg.Column(transformation_column, element_justification = "center", expand_y= True),   # column element
        ]
    ]

    window = sg.Window("Image Viewer", layout, font = font, resizable = True, finalize = True)   # this showcases the layout of our program in a window
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
            file_path = sg.popup_get_file(file_types =  # file types that are allowed for the application, this gets the file path of the image
            [
                ("PCX (*.pcx)", "*.pcx"),
                ("JPEG (*.jpg)", "*.jpg"),
                ("PNG (*.png)", "*.png"),
                ("GIF (*.gif)", "*.gif"), 
                ("All files (*.*)", "*.*")
            ], 
            no_window= True, message = "")

            window['-FILE-'].update(os.path.basename(file_path))    # this updates the input element-
                                                                    # (with the key '-FILE-') with the file name of the image

        elif event == "right":  # update the slider value 

            if(flag == 1):
                increment = round(values["-slider-"], 1)
                value = increment+1
                update_slider(value)

            elif(flag == 2):
                increment = round(values["-slider-"], 1)
                value = increment+0.1
                update_slider(value)           

        elif event == "left":

            if(flag == 1):
                decrement = round(values["-slider-"], 1)
                if (decrement != 0):
                    value = decrement-1
                    update_slider(value)
                
            elif(flag == 2):
                decrement = round(values["-slider-"], 1)
                if (decrement != 0):
                    value = decrement-0.1
                    update_slider(value)
                
        elif event == "-FILE LIST-":    # call image_open() whenever the the user clicks on the list box element
            try:
                clear_info()     
                file_list_name = values["-FILE LIST-"][0]     
                full_image, color_palette, image_dimensions = image_open(file_list_name)
                current_image = file_list_name
                clear_color_pallete(current_image)
            except:
                pass

        elif event == "Load Image":         # this  updates the file history whenever an image has been loaded,-
            clear_info()
            file_exist = values['-FILE-']      # and views the image
            
            if file_exist == "":
                pass
            elif not file_exist.endswith(('.gif', '.jpg', '.png', '.pcx', '.bmp')): # show error when user didn't choose an image
                sg.Popup("Please choose an image file.", font = font, button_type = 5, title = "Error!")
            else:
                file_list.append(file_path)     # if user has chosen a image, append its file path to the list inside the listbox,-
                window["-FILE LIST-"].update(file_list)    # and call image_open()
                if os.path.exists(file_path):
                    full_image, color_palette, image_dimensions = image_open(file_path)
                current_image = file_path
                clear_color_pallete(current_image)
            
        elif event == "R":    # show red channel [16]
            if current_image == "":         
                pass
            else:
                clear_info()
                clear_color_pallete(current_image)
                convert_to_RGB(current_image)   

                image = cv2.imread("tmp.png")   # cv2.imread() returns a BGR (Blue-Green-Red) array
                r = image.copy()
                r[:,:,0] = r[:,:,1] = 0     # extract the red channel of the image 
                cv2.imwrite("transformation.png", r)

                transformation("-transformation-", "-TRANSFORMATION-", "Red Channel:")  # display red channel and its histogram
                histogram(r)        
                
        elif event == "G":      # show the green channel [16]
            if current_image == "":
                pass
            else:
                clear_info()
                clear_color_pallete(current_image)
                convert_to_RGB(current_image)

                image = cv2.imread("tmp.png")   # cv2.imread() returns a BGR (Blue-Green-Red) array
                g = image.copy()
                g[:,:,0] = g[:,:,2] = 0     # extract the green channel of the image
                cv2.imwrite("transformation.png", g)

                transformation("-transformation-", "-TRANSFORMATION-", "Green Channel:")    # display green channel and its histogram
                histogram(g)     

        elif event == "B":       # show the blue channel [16]
            if current_image == "":
                pass
            else:
                clear_info()
                clear_color_pallete(current_image)
                convert_to_RGB(current_image)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                b = image.copy()
                b[:,:,1] = b[:,:,2] = 0     # extract the blue channel of the image
                cv2.imwrite("transformation.png", b)

                transformation("-transformation-", "-TRANSFORMATION-", "Blue Channel:")     # display blue channel and its histogram
                histogram(b)

        elif event == "grayscale":       # apply grayscale transformation [5]
            if current_image == "":
                pass
            else:
                clear_info()
                clear_color_pallete(current_image)
                convert_to_RGB(current_image)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                grayscale = image.copy()
                r, g, b = grayscale[:,:,2], grayscale[:,:,1], grayscale[:,:,0]  # get the values of each color channel 
                gray = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)     #  apply different set of weights for our channel averaging (weights taken from ITU-R 601-2 luma transform)                                                                        
                cv2.imwrite("transformation.png", gray)
               
                transformation("-transformation-", "-TRANSFORMATION-", "Grayscale Transformation:")   # display grayscale image
    
        elif event == "negative":       # apply negative transformation [6]
            if current_image == "":
                pass
            else:
                clear_info()
                clear_color_pallete(current_image)
                convert_to_RGB(current_image)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                negative = image.copy()
                negative = abs(255 - negative[:,:,:])   # subtract 255 by the value of each pixel in each color channels
                cv2.imwrite("transformation.png", negative)

                transformation("-transformation-", "-TRANSFORMATION-", "Negative Transformation:")  # display negatively transformed image
        
        elif event == "negative_grayscale":       # apply negative transformation of grayscale image [6]
            if current_image == "":
                pass
            else:
                clear_info()
                clear_color_pallete(current_image)
                convert_to_RGB(current_image)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                negative_grayscale = image.copy()
                r, g, b = negative_grayscale[:,:,2], negative_grayscale[:,:,1], negative_grayscale[:,:,0]  # get the red, green, and blue channels
                gray = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)     #  ITU-R 601-2 luma transform
                neg_gray = abs(255 - gray[:,:])     # subtract by 255 the value of each pixel in the grayscale image
                cv2.imwrite("transformation.png", neg_gray)

                transformation("-transformation-", "-TRANSFORMATION-", "Negative Transformation:")  # display negative transformation of grayscale image
        
        elif event == "b_and_w":       # apply black and white transformation
            if current_image == "":
                pass
            else:

                clear_info()
                clear_color_pallete(current_image)
                show_slider(255)

                png = Image.open(current_image).convert('RGBA')  # convert the image into RGBA
                background = Image.new("RGB", png.size, (255, 255, 255)) # create a white, blank image with the same dimensions as the input image 
                background.save('transformation.png', 'PNG')       # save the converted into a png file

                transformation("-transformation-", "-TRANSFORMATION-", "Black and White Transformation:")  # display the white, blank image 
                window["threshold"].update("B&W Threshold Value:")  

                flag = 1
                
        elif event == "gamma":       # apply gamma transformation 
            if current_image == "":
                pass
            else:

                clear_info() 
                clear_color_pallete(current_image)
                show_slider(20)        
                   
                convert_to_RGB(current_image)
                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                cv2.imwrite("transformation.png", image)     

                transformation("-transformation-", "-TRANSFORMATION-", "Gamma Transformation:")     # display the image   
                window["threshold"].update("Gamma Threshold Value:")

                flag = 2

        elif event == "Apply":       # apply black and white, or gamma transformation

            if (flag == 1):     # check if user clicked on button (with key "b_and_w")
                slider = int(math.floor(float(values["threshold_value"])))
              
                convert_to_RGB(current_image)

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
                transformation("-transformation-", "-TRANSFORMATION-", "Black and White Transformation:")   # display the black and white image 
                
            elif (flag == 2):    # check if user clicked on button (with key "gamma") [7] [8]
                slider = float(values["threshold_value"]) 
                
                convert_to_RGB(current_image)

                image = cv2.imread("tmp.png")   #   imread() returns a BGR (Blue-Green-Red) array
                gamma_transform = image.copy()
                gamma_transform = (255*(np.power((gamma_transform/255), (slider/4)))).clip(0, 255).astype(np.uint8) # s = cr^(γ/4), where c=1, r=[0,255], and γ is any value from 0-20
                                                                                                                    # s = 255*(c(r/255)^(γ/4))
                cv2.imwrite("transformation.png", gamma_transform)
                transformation("-transformation-", "-TRANSFORMATION-", "Gamma Transformation:")     # display the gamma transformed image 
            
        elif event == "spatial_filtering":       # apply black and white, or gamma transformation
            
            if current_image == "":
                pass
            else:
                convert_to_RGB(current_image)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                grayscale = image.copy()
                r, g, b = grayscale[:,:,2], grayscale[:,:,1], grayscale[:,:,0]  # get the values of each color channel 
                grayscale = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)     #  ITU-R 601-2 luma transform
                cv2.imwrite("transformation.png", grayscale)

                file_name = os.path.basename(current_image)  # get the image's filename only
                open_window(file_name, grayscale, full_image, color_palette, image_dimensions)
        
        elif event == "bit_plane":

            if current_image == "":
                pass
            else:
                convert_to_RGB(current_image)

                image = cv2.imread("tmp.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                grayscale = image.copy()
                r, g, b = grayscale[:,:,2], grayscale[:,:,1], grayscale[:,:,0]  # get the values of each color channel 
                grayscale = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)     #  ITU-R 601-2 luma transform
                cv2.imwrite("transformation.png", grayscale)

                open_bit_plane_window(current_image, grayscale)

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

# Sources:

# [1]
# TItle: Image Module (Pillow Documentation) 
# Author: Pillow
# Date: n.d.
# https://pillow.readthedocs.io/en/stable/reference/Image.html

# [2]
# Title: Convert RGBA PNG to RGB with PIL
# Author: Yuji 'Tomita' Tomita 
# Date: Feb. 27, 2012 
# URL: https://stackoverflow.com/questions/9166400/convert-rgba-png-to-rgb-with-pil

# [3]
# Title: Python - Calculate histogram of image 
# Author: Ondro
# Date: March 4, 2014
# URL: https://stackoverflow.com/questions/22159160/python-calculate-histogram-of-image

# [4]
# Title: 2. Histogram Calculation in Numpy 
# Author: OpenCV
# Date: n.d.
# https://docs.opencv.org/4.x/d1/db7/tutorial_py_histogram_begins.html#:~:text=Histogram%20Calculation%20in%20Numpy&text=But%20bins%20will%20have%20257,256%20at%20end%20of%20bins.

# [5]
# Title: How can I convert an RGB image into Grayscale in Python? 
# Author: waspinator
# Date: Aug 30, 2012 
# https://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python

# [6]
# Title: How to Generate a Negative Image in Python using OpenCV 
# Author: Abhishek Sharma
# Date: Feb. 2, 2022
# URL: https://medium.com/mlearning-ai/how-to-generate-a-negative-image-in-python-using-opencv-interesting-project-439da0c19544

# [7]
# Title: How to Set the Best Value for Gamma Correction 
# Author: fmw42
# Date: May 9, 2020
# https://stackoverflow.com/questions/61695773/how-to-set-the-best-value-for-gamma-correction

# [8]
# Title: Python | Intensity Transformation Operations on Images
# Author: GeeksForGeeks
# Date: Aug. 2, 2019
# URL: https://www.geeksforgeeks.org/python-intensity-transformation-operations-on-images/

# [9]
# Title: Spatial Filters – Averaging filter and Median filter in Image Processing
# Author: GeeksForGeeks
# Date: Nov. 9, 2021
# URL: https://www.geeksforgeeks.org/spatial-filters-averaging-filter-and-median-filter-in-image-processing/

# [10]
# Title: Add a “salt and pepper” noise to an image with Python
# Author: GeeksForGeeks
# Date: Oct. 27, 2021
# URL: https://www.geeksforgeeks.org/add-a-salt-and-pepper-noise-to-an-image-with-python/#:~:text=Salt%2Dand%2Dpepper%20noise%20is,%2C%20bit%20transmission%20error%2C%20etc.&text=Below%20is%20the%20implementation%3A,Python

# [11]
# Title: Python#9 Frequency Domain Image Filter using Laplacian Filter in Python
# Author: Made Python
# Date: June 22, 2022
# URL: https://www.youtube.com/watch?v=i-Rvo48vBKA

# [12]
# Title: Python#11 Unsharp Masking and Highboost Filterin in Spatial Domain
# Author: Made Python
# Date: July 23, 2022
# URL: https://www.youtube.com/watch?v=IpqZ7D1km5g

# [13]
# Title: Python#10 Laplacian Filter in Spatial Domain using Python
# Author: Made Python
# Date: July 13, 2022
# URL: https://www.youtube.com/watch?v=5l0y-LMM1c0

# [14]
# Title: Python#13 Edge Detection using Sobel Operator in Python
# Author: Alexandre Damião
# Date: Jun 3, 2019
# URL: https://www.youtube.com/watch?v=eifdexvpnq0

# [15]
# Title: PCX
# Author: Wikipedia
# Date: n.d.
# URL: https://en.wikipedia.org/wiki/PCX

# [16]
# Title: How to extract individual channels from an RGB image
# Author: nathancy
# Date: Aug 7, 2019
# URL: https://stackoverflow.com/questions/57398643/how-to-extract-individual-channels-from-an-rgb-image

# [17]
# Title: EL5123 - Image Processsing
# Author: Yao Wong
# Date: n.d.
# URL: https://eeweb.engineering.nyu.edu/~yao/EL5123/lecture7_median_morph.pdf

# [18]
# Title: Introduction to Image Processing in Python with OpenCV
# Author: Muhammad Junaid Khalid
# URL: https://stackabuse.com/introduction-to-image-processing-in-python-with-opencv/

# [19]
# Title: Extract bit planes from an Image in Matlab
# Author: GeeksforGeeks
# Date: May 28, 2017
# URL: https://www.geeksforgeeks.org/extract-bit-planes-image-matlab/

# [20]
# Title: Python Program to Convert Binary to Decimal
# Author: CodesCracker
# Date: n.d.
# URL: https://codescracker.com/python/program/python-program-convert-binary-to-decimal.htm

# [21]
# Title: RLE (Run-Length Encoding) compression for Images
# Author: Coding Adventures
# Date: June 22, 2022
# URL: https://www.youtube.com/watch?v=QXfhaeIXZRo&t=1770s
