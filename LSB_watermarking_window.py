# File Description: functions for dealing with watermarking through bit-plane slicing
# Author: John Cedric R. Warain, 4 - BSCS

from re import L
from tkinter import Y
import cv2      # import modules 
import os
from os.path import exists
import PySimpleGUI as sg
import struct 
import matplotlib.pyplot as plt   
from PIL import Image, ImageTk  #Image for open, ImageTk for display
import numpy as np

# function for dealing with watermarking through bit-plane slicing
def open_bit_plane_window(file_path, original_grayscale): 

    sg.theme('DarkGrey8')   # theme of the program
    font = ("04b03", 12)     # font style of the program

    # function for displaying an image
    def transformation(transform_name, transform_image, transformation, open_image):
        image = Image.open(open_image)     # open the transformed image
        image.thumbnail((256, 256))     # resize the image
        window[transform_name].update(transformation)   
        window[transform_image].update(data = ImageTk.PhotoImage(image))    # display the image's respective transformation

    # function for opening an image which is not a PCX file
    def watermark_to_RGB(file):     
        file_name = os.path.basename(file)  # get the image's filename only
        
        if(file_name.split(".")[1] == "png"):    # check if image is in PNG format [1] [2]
            png = Image.open(file).convert('RGBA')  # convert the image into RGBA
            png.load()               # required for png.split()
            background = Image.new("RGB", png.size, (255, 255, 255)) # if the image has a transparent background, turn the background white
            background.paste(png, mask=png.split()[3])      # 3 is the alpha channel
            background.save('watermark.png', 'PNG')       # save the converted into a png file 

        elif(file_name.split(".")[1] != "pcx"):     # every other image format besides .png and .pcx
            image = Image.open(file)       # open the image
            RGB_image = image.convert("RGB")        # convert the image into RGB
            RGB_image.save("watermark.png")           # save the converted into a png file

    # function for opening a PCX image
    def open_PCX(file):   # function for opening an image
        
        file_name = os.path.basename(file)  # get the image's filename only

        if(file_name.split(".")[1] == "pcx"):    # check if image is not in PCX format
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
                
                imageData.save("watermark.png")

            f.close()

    # function for getting the bit plane of the image [19]
    def bit_plane_slicing(number, bit_plane_list):
        grayscale = np.floor(original_grayscale / number) % 2       
        grayscale[grayscale == 1] = 255
        cv2.imwrite("bit_plane_slice.png", grayscale)
        grayscale[grayscale == 255] = 1
        bit_plane_list.append(grayscale)
    
    # function for converting binary to decimal [20]
    def binToDec(bnum):
        bnum = int(bnum)
        dnum = 0
        i = 1
        while bnum!=0:
            rem = bnum%10
            dnum = dnum + (rem*i)
            i = i*2
            bnum = int(bnum/10)
            
        return dnum

    options_column = [              # these columns are displaying the images
        [sg.Button('Apply Watermark', key='watermark_image', pad = ((5, 0), (0, 0))),],
    ]
    
    second_column = [               
        [sg.Text("Bit Plane 0:", key='first', size = (40, 1), pad=((0, 0), (0, 4)), text_color = "yellow", justification = 'center')],    
        [sg.Image(key="-first_image-", pad = ((0, 0), (0, 10)), size = (320, 240), filename="empty.png")],   # image element
        [sg.Text("Bit Plane 4:", key='fifth', size = (40, 1), text_color = "yellow", justification = 'center')],     
        [sg.Image(key="-fifth_image-", size = (320, 240), filename="empty.png")],   
        [sg.Text("Watermarked Image:", key='watermark', size = (40, 1), text_color = "yellow", justification = 'center')],     
        [sg.Image(key="-watermark_image-", size = (320, 240), filename="empty.png")],   
    ]

    third_column = [
        [sg.Text("Bit Plane 1:", key='second', size = (40, 1), pad=((0, 0), (0, 4)), text_color = "yellow", justification = 'center')],    
        [sg.Image(key="-second_image-", pad = ((0, 0), (0, 10)), size = (320, 240), filename="empty.png")],   # image element
        [sg.Text("Bit Plane 5:", key='sixth', size = (40, 1), text_color = "yellow", justification = 'center')],     
        [sg.Image(key="-sixth_image-", size = (320, 240), filename="empty.png")],   
    ]

    fourth_column = [
        [sg.Text("Bit Plane 2:", key='third', size = (40, 1), pad=((0, 0), (0, 4)), text_color = "yellow", justification = 'center')],    
        [sg.Image(key="-third_image-", pad = ((0, 0), (0, 10)), size = (320, 240), filename="empty.png")],   # image element
        [sg.Text("Bit Plane 6:", key='seventh', size = (40, 1), text_color = "yellow", justification = 'center')],     
        [sg.Image(key="-seventh_image-", size = (320, 240), filename="empty.png")],   
    ]

    fifth_column = [
        [sg.Text("Bit Plane 3:", key='fourth', size = (40, 1), pad=((0, 0), (0, 4)), text_color = "yellow", justification = 'center')],    
        [sg.Image(key="-fourth_image-", pad = ((0, 0), (0, 10)), size = (320, 240), filename="empty.png")],   # image element
        [sg.Text("Bit Plane 7:", key='eighth', size = (40, 1), text_color = "yellow", justification = 'center')],     
        [sg.Image(key="-eighth_image-", size = (320, 240), filename="empty.png")],   
    ]

    layout = [      # this defines the window's contents
        [
            sg.Column(options_column, vertical_alignment='center', p = ((0, 3), (60, 75))),    # column element
            sg.VSeperator(),       # this is a vertical line that shows the separation of the columns
            sg.Column(second_column, element_justification = "center", pad = ((0, 0), (8, 20)), expand_y= True),   # column element
            sg.Column(third_column, element_justification = "center", pad = ((0, 0), (8, 20)), expand_y= True),   # column element
            sg.Column(fourth_column, element_justification = "center", pad = ((0, 0), (8, 20)), expand_y= True),   # column element
            sg.Column(fifth_column, element_justification = "center", pad = ((0, 0), (8, 20)), expand_y= True),   # column element
        ]
    ]
    
    window = sg.Window("LSB Watermarking", layout, font = font, resizable = True, finalize = True, modal=True, size=(1750, 950))    # open a window on top of the original window
    
    bit_plane_list = []         # a list stores value of the bit planes
    bit_plane_slicing(1, bit_plane_list)        # get and display bit plane zero (0)
    transformation("first", "-first_image-", "Bit Plane 0:", "bit_plane_slice.png")

    while True:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
        elif event == "watermark_image":

            bit_plane_list = []             # a list stores value of the bit planes         
            bit_plane_slicing(1, bit_plane_list)        # get and display the rest of the bit planes from zero (0) to seven (7)
            transformation("first", "-first_image-", "Bit Plane 0:", "bit_plane_slice.png")
            
            bit_plane_slicing(2, bit_plane_list)
            transformation("second", "-second_image-", "Bit Plane 1:", "bit_plane_slice.png")

            bit_plane_slicing(4, bit_plane_list)
            transformation("third", "-third_image-", "Bit Plane 2:", "bit_plane_slice.png")

            bit_plane_slicing(8, bit_plane_list)
            transformation("fourth", "-fourth_image-", "Bit Plane 3:", "bit_plane_slice.png")

            bit_plane_slicing(16, bit_plane_list)
            transformation("fifth", "-fifth_image-", "Bit Plane 4:", "bit_plane_slice.png")

            bit_plane_slicing(32, bit_plane_list)
            transformation("sixth", "-sixth_image-", "Bit Plane 5:", "bit_plane_slice.png")

            bit_plane_slicing(64, bit_plane_list)
            transformation("seventh", "-seventh_image-", "Bit Plane 6:", "bit_plane_slice.png")

            bit_plane_slicing(128, bit_plane_list)
            transformation("eighth", "-eighth_image-", "Bit Plane 7:", "bit_plane_slice.png")

            file_path = sg.popup_get_file(file_types =  # file types that are allowed for the application, this gets the file path of the image
            [
                ("PCX (*.pcx)", "*.pcx"),
                ("JPEG (*.jpg)", "*.jpg"),
                ("PNG (*.png)", "*.png"),
                ("GIF (*.gif)", "*.gif"), 
                ("All files (*.*)", "*.*")
            ], 
            no_window= True, message = "")

            if file_path == "":
                pass
            else:
                watermark_to_RGB(file_path)     # display the image
                open_PCX(file_path)

                image = cv2.imread("watermark.png")   #   cv2.imread() returns a BGR (Blue-Green-Red) array
                grayscale = image.copy()
                r, g, b = grayscale[:,:,2], grayscale[:,:,1], grayscale[:,:,0]  # get the values of each color channel 
                grayscale = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)     #  ITU-R 601-2 luma transform
                
                rows, cols = grayscale.shape     # get the dimensions of the image
                for x in range(rows):
                    for y in range(cols):
                        if(grayscale[x][y] >= 128):   # compare grayscale value of the pixels to 128 
                            grayscale[x][y] =  255       # if above or equal to 128, turn the pixel white
                        else:
                            grayscale[x][y] =  0         # if below 128, turn the pixel black
                
                cv2.imwrite("watermark.png", grayscale)     

                grayscale = grayscale / 255
                
                if ((grayscale.shape) != (bit_plane_list[0].shape)):      # stop program if chosen watermark is not of the same dimensions as bit plane zero
                    sg.Popup("Please use a watermark with same dimensions.", font = font, button_type = 5, title = "Error!")
                else:
                    bit_plane_list[0] = grayscale           # replace bit plane zero with grayscale
                    watermarked_image = []
                    full_image = []

                    for x in range(len(bit_plane_list)-1, -1, -1):      # convert the bit planes into lists
                        bit_plane_list[x] = bit_plane_list[x].reshape(bit_plane_list[x].shape[0] * bit_plane_list[x].shape[1])
                        bit_plane_list[x] = list(np.uint8(bit_plane_list[x]))
                    
                    for y in range(len(bit_plane_list[7])):         # append the elements in the list to an empty list to store the binary numbers that represent the color of the pixels in the image
                        watermarked_image.append(str(bit_plane_list[7][y]) + str(bit_plane_list[6][y]))
                    
                    for y in range(len(bit_plane_list[5])):
                        watermarked_image[y] = watermarked_image[y] + (str(bit_plane_list[5][y]) + str(bit_plane_list[4][y]))

                    for y in range(len(bit_plane_list[3])):
                        watermarked_image[y] = watermarked_image[y] + (str(bit_plane_list[3][y]) + str(bit_plane_list[2][y]))
                    
                    for y in range(len(bit_plane_list[1])):
                        watermarked_image[y] = watermarked_image[y] + (str(bit_plane_list[1][y]) + str(bit_plane_list[0][y]))
                    
                    for y in range(len(watermarked_image)):        # convert the binary numbers into integers
                        binary = watermarked_image[y]
                        number = binToDec(binary)
                        full_image.append(number)

                    full_image = np.array(full_image)          # convert the list back to an array to display it as an watermarked image
                    full_image = full_image.reshape(rows, cols)
                    cv2.imwrite("watermark_image.png", full_image)
                    
                    transformation("first", "-first_image-", "Replaced Bit Plane 0:", "watermark.png")
                    transformation("watermark", "-watermark_image-", "Watermarked Image:", "watermark_image.png")

    window.close()    

    