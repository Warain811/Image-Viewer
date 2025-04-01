# File Description: functions for dealing with spatial transformations, image restoration, and image compression
# Author: John Cedric R. Warain, 4 - BSCS

from re import L
from tkinter import Y
import cv2      # import modules
from os.path import exists
import PySimpleGUI as sg 
import matplotlib.pyplot as plt   
from PIL import Image, ImageTk  #Image for open, ImageTk for display
import numpy as np
import random

def open_window(file_name, original_grayscale, RGB_full_image, RGB_color_palette, RGB_image_dimensions): 
   
    sg.theme('DarkGrey8')   # theme of the program
    font = ("04b03", 12)     # font style of the program
    
    # function for the decompression algorithm for RGB
    def decompress_rgb(byte_data, ColorPalette):
        
        imageData = Image.new('RGB', (RGB_image_dimensions.shape[1], RGB_image_dimensions.shape[0]), "black")   # create a completely black 256x256 image for printing the actual image
        pixels = imageData.load()   # load the pixel map
        
        imageColorValues = [[0 for x in range(3)] for y in range(RGB_image_dimensions.shape[1] * RGB_image_dimensions.shape[0])]    # the list will store height, width, and channel depth 
        paletteIndex = []
        position = 0
        runlength = 0
        runvalue = 0

        while (position < int(len(byte_data)) ):  # this range represents where the image data is located ( 128 bytes < position < (byte_data - 768))
            Byte = byte_data[position]   
            position = position + 1
           
            if ((Byte & 0xC0) == 0xC0 and position < (len(byte_data))):  # RLE pair representing a series of several pixels of a single value
                runlength = (Byte & 0x3F)            # run length have a value range of 0-63, and its length can be extracted through bitwise addition 
                runvalue = int(byte_data[position])          # run value represents the given palette index for the pixels
                position = position + 1

            else:   # any other case, the byte is interpreted as a single pixel value of a given palette index or color value
                runlength = 1
                runvalue = Byte 
            
            for j in range(0, runlength):
                paletteIndex.append(runvalue)
        
        for i in range(0, RGB_image_dimensions.shape[0] * RGB_image_dimensions.shape[1]):
            imageColorValues[i] = ColorPalette[paletteIndex[i]] # get the color from the color palette
            y = int(i / RGB_image_dimensions.shape[1])                # get the x and y coordinate for the pixel  
            x = int(i - (RGB_image_dimensions.shape[1] * y))
            pixels[x, y] = (imageColorValues[i][0], imageColorValues[i][1], imageColorValues[i][2]) # set the  color of the pixel in the appropriate pixel map
        
        imageData.save("decompressed.png")
    
    # function for the decompression algorithm for grayscale
    def decompress_grayscale(compressed_data_grayscale, grayscale_color_palette, image_shape):  
      
        decompressed_data_grayscale = []
        i = 0
        
        while(i < int(len(compressed_data_grayscale))): # loop through entire image

            image_pixel = compressed_data_grayscale[i]
            count = 1

            if image_pixel == 0:        # image_pixel is zero (0)- zero (0) is a marker meaning the-
                                        # next two sequence of integers are the runlength and runvalues, respectively
                count = 0
                if (i < int(len(compressed_data_grayscale))-1):
                    i = i + 1   
                    image_pixel = compressed_data_grayscale[i]     # get the runvalue
                    
                if (i < int(len(compressed_data_grayscale))-1):
                    i = i + 1
                    count = compressed_data_grayscale[i]        # get the runlength

            for j in range(len(grayscale_color_palette)):
                if image_pixel == j:
                    palette_color = grayscale_color_palette[j]      # get the color that based from the palette index
                    break
            
            for m in range(count):
                decompressed_data_grayscale.append(palette_color)       # append to a decompressed_data_grayscale list

            if(i < int(len(original_grayscale_image))):     # proceed to the next iteration in the list
                i = i + 1
            else:
                break
        
        decompressed_data_grayscale = np.array(decompressed_data_grayscale)
        decompressed_data_grayscale = decompressed_data_grayscale.reshape(image_shape[0], image_shape[1])  # image_shape[0] is height, image_shape[1] is width
        cv2.imwrite("decompressed.png", decompressed_data_grayscale)

    def transformation(transform_name, transform_image, transformation, open_image): # function for the opening an image
        image = Image.open(open_image)     # open the transformed image
        image.thumbnail((256, 256))     # resize the image
        window[transform_name].update(transformation)   
        window[transform_image].update(data = ImageTk.PhotoImage(image))    # display the image's respective transformation
    
    def clear_info(grayscale):           # function to clear and hide widgets whenever another image has been viewed 
        cv2.imwrite('transformation.png', grayscale)
        transformation("first", "-first_image-", "Original Image:", "transformation.png")     # display the image
        window["second"].update('')  
        window["-second_image-"].update('')     
        window["third"].update('')   
        window["-third_image-"].update('')
        window["fourth"].update('')   
        window["-fourth_image-"].update('')  

    def unsharp_masked_image(k):       # function for the unsharp masked transformation
        unsharp_masking = original_image + k * mask  # add the mask to the original image
        unsharp_masking = np.clip(unsharp_masking, 0, 1)     # clip the values within 0 to 1
        unsharp_masking[:] = unsharp_masking[:] * 255
        cv2.imwrite('transformation.png', unsharp_masking)

    def contraharmonic(Q):      # function for contraharmonic mean filter
        original_image = np.array(grayscale) / 255      # normalize the image    
        kernel = np.array([ [1, 1, 1],          # create the filter mask  
                            [1, 1, 1],
                            [1, 1, 1] ])
        output = apply_power_filter(original_image, Q, kernel)    # apply the filter to the images to get the output image
        return (output * 255)

    def apply_power_filter(original_image, Q, kernel):
        # Add small epsilon to avoid divide by zero
        eps = 1e-10
        original_image = original_image.astype(np.float64) + eps
        
        num = np.power(original_image, Q + 1)
        denom = np.power(original_image, Q)
        
        # Apply filter and handle potential division by zero
        filtered_num = cv2.filter2D(src=num, ddepth=-1, kernel=kernel)
        filtered_denom = cv2.filter2D(src=denom, ddepth=-1, kernel=kernel)
        
        # Avoid division by zero
        output = np.zeros_like(filtered_num)
        mask = filtered_denom != 0
        output[mask] = filtered_num[mask] / filtered_denom[mask]
        
        return output

    def apply_laplacian_sharpening(grayscale, c, LaplacianMask):
        """Apply Laplacian sharpening to an image.
        
        Args:
            grayscale: Input grayscale image
            c: Sharpening constant
            LaplacianMask: Laplacian mask
            
        Returns:
            Sharpened image as uint8
        """
        # Convert inputs to float64 for calculations
        grayscale = grayscale.astype(np.float64)
        LaplacianMask = LaplacianMask.astype(np.float64)
        
        # Perform sharpening operation
        result = grayscale + c * LaplacianMask
        
        # Clip values to valid range and convert back to uint8
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)

    filter_column = [
        [sg.Button('Original Image', key = 'original_image', pad = ((5, 0), (0, 0))),],
        [sg.Button('Salt and Pepper Noise', key = 'salt_and_pepper', pad = ((5, 0), (10, 0)), border_width = 1, tooltip=" Apply Salt and Pepper Noise ")],
        [sg.Button('Salt Noise', key = 'salt', pad = ((5, 0), (10, 0)), border_width = 1, tooltip=" Apply Salt Noise ")],
        [sg.Button('Pepper Noise', key = 'pepper', pad = ((5, 0), (10, 10)), border_width = 1, tooltip=" Apply Pepper Noise ")],
        [sg.Text("Filter Options:", size = (40, 1), text_color = "yellow", justification='center')], 
        [sg.Button('Lowpass Filters', key = 'lowpass', pad = ((5, 0), (10, 0)), border_width = 1)],
        [sg.Button('Laplacian', key = 'laplacian', pad = ((5, 0), (10, 0)), border_width = 1)],
        [sg.Button('Unsharp Masking', key = 'unsharp_masking', pad = ((5, 0), (10, 0)), border_width = 1)],
        [sg.Button('Highboost Filtering', key = 'highboost', pad = ((5, 0), (10, 0)), border_width = 1)],
        [sg.Button('Gradient', key = 'gradient', pad = ((5, 0), (10, 10)), border_width = 1)],
        [sg.Text("Image Restoration Options:", size = (40, 1), text_color = "yellow", justification='center')],
        [sg.Button('Contraharmonic Mean Filter (Q=-1.5)', key = 'elim_salt_contra', pad = ((5, 0), (10, 0)), border_width = 1, tooltip=" Eliminate Salt Noise Through Contraharmonic Mean Filter ")],
        [sg.Button('Contraharmonic Mean Filter (Q=1.5)', key = 'elim_pepper_contra', pad = ((5, 0), (10, 0)), border_width = 1, tooltip=" Eliminate Pepper Noise Through Contraharmonic Mean Filter ")],   
        [sg.Button('Min Filter', key = 'min_filter', pad = ((5, 0), (10, 0)), border_width = 1, tooltip=" Eliminate Salt Noise Through Min Filter ")],        
        [sg.Button('Max Filter', key = 'max_filter', pad = ((5, 0), (10, 10)), border_width = 1, tooltip=" Eliminate Pepper Noise Through Max Filter ")],
        [sg.Text("Image Compression Options:", size = (40, 1), text_color = "yellow", justification='center')],
        [sg.Button('RLE for Grayscale', key = 'run_length_grayscale', pad = ((5, 0), (10, 0)), border_width = 1)],
        [sg.Button('RLE for RGB', key = 'run_length_rgb', pad = ((5, 0), (10, 0)), border_width = 1)],
    ]

    second_column = [
        [sg.Text("Original Image:", key='first', size = (50, 1), pad=((0, 0), (0, 8)), text_color = "yellow", justification = 'center')],    
        [sg.Image(key="-first_image-", pad = ((0, 0), (0, 10)), size = (320, 240), filename="empty.png")],   # image element
        [sg.Text("Third Image:", key='third', size = (50, 1), text_color = "yellow", justification = 'center')],     
        [sg.Image(key="-third_image-", size = (320, 240), filename="empty.png")],   
    ]

    third_column = [
        [sg.Text("Second Image:", key='second', size = (50, 1), pad=((0, 0), (0, 8)), text_color = "yellow", justification = 'center')],     
        [sg.Image(key="-second_image-", pad = ((0, 0), (0, 10)), size = (320, 240), filename="empty.png")],  
        [sg.Text("Fourth Image:", key='fourth', size = (50, 1), text_color = "yellow", justification = 'center')],    
        [sg.Image(key="-fourth_image-", pad = ((0, 0), (0, 0)), size = (320, 240), filename="empty.png")],   
    ]

    layout = [      # this defines the window's contents
        [
            sg.Column(filter_column, vertical_alignment='center', p = ((0, 3), (60, 75))),    # column element
            sg.VSeperator(),       # this is a vertical line that shows the separation of the columns
            sg.Column(second_column, element_justification = "center", pad = ((0, 0), (8, 25)), expand_y= True),   # column element
            sg.Column(third_column, element_justification = "center", pad = ((0, 0), (8, 25)), expand_y= True),   # column element
        ]
    ] 

    grayscale = np.array(original_grayscale)
    window = sg.Window("Spatial Filtering", layout, font = font, resizable = True, finalize = True, modal=True, size=(1400, 830))
    transformation("first", "-first_image-", "Original Image:", "transformation.png")     # display the gamma transformed image 

    while True:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        elif event == "original_image":   # use the original grayscale image

            cv2.imwrite('transformation.png', original_grayscale)
            grayscale = np.array(original_grayscale)
            transformation("first", "-first_image-", "Original Image:", "transformation.png")     # display the gamma transformed image 

        elif event == "salt_and_pepper":   # apply salt and pepper noise to the image [10]
            col, row = grayscale.shape[0], grayscale.shape[1]  # col is the height, while row is width

            number_of_pixels = int((col * row) / 80)

            for i in range(number_of_pixels):
                x_coord = random.randint(0, col - 1)   # pick a random x-coordinate
                y_coord = random.randint(0, row - 1)   # pick a random y-coordinate
                grayscale[x_coord][y_coord] = 255    # color the pixel into white
            
            number_of_pixels = int((col * row) / 80)

            for i in range(number_of_pixels):
                x_coord = random.randint(0, col - 1)   # pick a random x-coordinate
                y_coord = random.randint(0, row - 1)   # pick a random y-coordinate
                grayscale[x_coord][y_coord] = 0    # color the pixel into black

            cv2.imwrite('transformation.png', grayscale)
            transformation("first", "-first_image-", "Original Image:", "transformation.png")     # display the image
        
        elif event == "salt":   # apply salt noise to the image [10]
            col, row = grayscale.shape[0], grayscale.shape[1]  # col is the height, while row is width

            number_of_pixels = int((col * row) / 40)

            for i in range(number_of_pixels):
                x_coord = random.randint(0, col - 1)   # pick a random x-coordinate
                y_coord = random.randint(0, row - 1)   # pick a random y-coordinate
                grayscale[x_coord][y_coord] = 255    # color the pixel into white

            cv2.imwrite('transformation.png', grayscale)
            transformation("first", "-first_image-", "Original Image:", "transformation.png")     # display the image
        
        elif event == "pepper":   # apply pepper noise to the image [10]
            col, row = grayscale.shape[0], grayscale.shape[1]  # col is the height, while row is width

            number_of_pixels = int((col * row) / 40)

            for i in range(number_of_pixels):
                x_coord = random.randint(0, col - 1)   # pick a random x-coordinate
                y_coord = random.randint(0, row - 1)   # pick a random y-coordinate
                grayscale[x_coord][y_coord] = 0    # color the pixel into black

            cv2.imwrite('transformation.png', grayscale)
            transformation("first", "-first_image-", "Original Image:", "transformation.png")     # display the image
        
        elif event == "lowpass":   # apply the lowpass spatial filters 
            clear_info(grayscale)  
            
            # apply the weighted average filter [9] 
            rows, columns = grayscale.shape[0], grayscale.shape[1]  # rows is the height, while columns is width
            mask = np.array([ [1, 2, 1],          # create the weighted average filter mask  
                                [2, 4, 2],
                                [1, 2, 1] ])
            mask = mask / 16

            weightAverage = np.zeros([rows-2, columns-2])       # create a pixel map

            for i in range(rows - 2):
                for j in range(columns - 2):         # apply filter to the input image 
                    weightAverage[i, j] = np.sum(np.multiply(mask, grayscale[i:i + 3, j:j + 3]))   

            weightAverage = weightAverage.astype(np.uint8)      # set the intensity value of each pixel in the output image as an unsigned 8-bit integer
            
            cv2.imwrite('transformation.png', weightAverage)
            transformation("second", "-second_image-", "Weighted Average Filter:", "transformation.png")     # display the filtered image 

            # apply the median filter  [9] [17]
            rows, columns = grayscale.shape[0], grayscale.shape[1]  # rows is the height, while columns is width
            mask = np.array([ [1, 1, 1],          # create the median-square filter mask  
                                [1, 1, 1],
                                [1, 1, 1] ])

            medianFilter = np.zeros([rows-2, columns-2])
            
            for i in range(rows-2):
                for j in range(columns-2):   # apply filter to the input image
                    temp = np.multiply(mask, grayscale[i:i + 3, j:j + 3])
                    temp = sorted(temp.astype(np.uint8).flatten())
                    medianFilter[i, j]= temp[4]

            cv2.imwrite('transformation.png', medianFilter)
            transformation("third", "-third_image-", "Median Square Filter:", "transformation.png")     # display the filtered image 

            mask = np.array([ [0, 1, 0],          # create the median-cross filter mask  
                                [1, 1, 1],
                                [0, 1, 0] ])

            medianFilter = np.zeros([rows-2, columns-2])
            
            for i in range(rows-2):
                for j in range(columns-2):   # apply filter to the input image
                    temp = np.multiply(mask, grayscale[i:i + 3, j:j + 3])
                    temp = sorted(temp.astype(np.uint8).flatten())
                    medianFilter[i, j]= temp[6]

            cv2.imwrite('transformation.png', medianFilter)
            transformation("fourth", "-fourth_image-", "Median Cross Filter:", "transformation.png")     # display the filtered image 

        elif event == "laplacian":   # use the laplacian filter for image sharpening  
            clear_info(grayscale)

            # apply the laplacian filter in frequency domain for image sharpening  [11]
            laplacian_grayscale = np.array(grayscale) / 255     # open and normalize the image          
            F = np.fft.fftshift(np.fft.fft2(laplacian_grayscale))     # transform into frequency domain

            # create the laplacian Filter
            P, Q = F.shape  # P is height, Q is width
            H = np.zeros((P,Q), dtype=np.float32)
            for u in range(P):
                for v in range(Q):
                    H[u,v] = -4*np.pi*np.pi*((u-P/2)**2 + (v-Q/2)**2)       # laplacian transfer filter function

            # create the laplacian image
            Lap = H * F
            Lap = np.fft.ifftshift(Lap)
            Lap = np.real(np.fft.ifft2(Lap))

            # convert the laplacian image value into range [-1,1]
            OldRange = np.max(Lap) - np.min(Lap)
            NewRange = 1 - -1
            LapScaled = (((Lap - np.min(Lap)) * NewRange) / OldRange) + -1
                    
            # sharpen the image
            c = -1
            sharpenedImage = laplacian_grayscale + c*LapScaled
            sharpenedImage = np.clip(sharpenedImage, 0, 1)

            sharpenedImage[:] = sharpenedImage[:] * 255     

            cv2.imwrite('transformation.png', sharpenedImage)
            transformation("second", "-second_image-", "Laplacian Filter in Frequency Domain:", "transformation.png")     # display the filtered image 

            # apply the laplacian filter in spatial domain for image sharpening  [13]
            laplacian_grayscale = np.array(grayscale)

            kernel = np.array([[0, 1, 0],               # filter mask for cv2.filter
                                [1, -4, 1],
                                [0, 1, 0]])
            
            LaplacianMask = cv2.filter2D(src = laplacian_grayscale,   # cv2.filter2D creates the laplacian mask
                                        ddepth = -1,                   # the output is the same size as the input image since- 
                                        kernel = kernel)               # cv2.filter2D adds padding

            c = -1
            sharpenedImage = apply_laplacian_sharpening(laplacian_grayscale, c, LaplacianMask)

            cv2.imwrite('transformation.png', sharpenedImage)
            transformation("third", "-third_image-", "Laplacian Filter in Spatial Domain:", "transformation.png")     # display the filtered image

        elif event == "unsharp_masking":   # apply the unsharp masking for image sharpening  [12]
            clear_info(grayscale)
            original_image = np.array(grayscale) / 255     # normalize the original image          
            
            blurred_image = cv2.GaussianBlur(src=original_image,  # create a blurred image
                                    ksize=(31,31),  # gaussian smoothing filter of size 31x31 with a standard deviation of 5 
                                    sigmaX=5, 
                                    sigmaY=5)

            mask = original_image - blurred_image   # subtract the blurred image from the original (the resulting difference is the mask)
            
            unsharp_masked_image(k=1)
            transformation("second", "-second_image-", "Unsharp Masking:", "transformation.png")     # display the filtered image 
        
        elif event == "highboost":   # apply the highboost filtering for image sharpening  [12]
            clear_info(grayscale)

            original_image = np.array(grayscale) / 255     # normalize the image          
            
            blurred_image = cv2.GaussianBlur(src=original_image, # create a blurred image
                                    ksize=(31,31),  # kernel size of 31x31
                                    sigmaX=0, 
                                    sigmaY=0)

            mask = original_image - blurred_image   # subtract the blurred image from the original (the resulting difference is the mask)
            
            k=2
            unsharp_masked_image(k)
            transformation("second", "-second_image-", "Highboost Filtering (k="+str(k)+"):", "transformation.png")     # display the filtered image 

            k=5
            unsharp_masked_image(k)
            transformation("third", "-third_image-", "Highboost Filtering (k="+str(k)+"):", "transformation.png")     # display the filtered image

            k=10
            unsharp_masked_image(k)
            transformation("fourth", "-fourth_image-", "Highboost Filtering (k="+str(k)+"):", "transformation.png")     # display the filtered image 
        
        elif event == "gradient":   # apply the gradient for image sharpening  [14]
            clear_info(grayscale)

            original_image = np.array(grayscale)

            sobel_x = np.array([[-1, 0, 1],  # sobel kernels
                                [-2, 0, 2],
                                [-1, 0, 1]])

            sobel_y =  np.array([[-1, -2, -1],   
                                [ 0,  0,  0],
                                [ 1,  2,  1]])
                                
            original_image = (255*(np.power((original_image/255), (1.4)))).clip(0, 255).astype(np.uint8) # apply gamma to the image

            [rows, columns] = np.shape(original_image)  # shape of the input grayscale image
            sobel_filtered_image = np.zeros([rows-2, columns-2])  # initialization of the output image array (all elements are 0)
            sobel_x_gradient = np.zeros([rows-2, columns-2])  
            sobel_y_gradient = np.zeros([rows-2, columns-2])  

            # "sweep" the image in both x and y directions and compute the output
            for i in range(rows - 2):
                for j in range(columns - 2):
                    gx = np.sum(np.multiply(sobel_x, original_image[i:i + 3, j:j + 3]))  # get x partial derivative
                    gy = np.sum(np.multiply(sobel_y, original_image[i:i + 3, j:j + 3]))  # get y partial derivative
                    sobel_x_gradient[i, j] = gx 
                    sobel_y_gradient[i, j] = gy  
                    sobel_filtered_image[i, j] = np.sqrt(gx ** 2 + gy ** 2)  

            plt.imsave('transformation.png', sobel_x_gradient, cmap='gray')
            transformation("second", "-second_image-", "Sobel X-Gradient:", "transformation.png")     # display the sobel x-gradient image

            plt.imsave('transformation.png', sobel_y_gradient, cmap='gray')
            transformation("third", "-third_image-", "Sobel Y-Gradient:", "transformation.png")     # display the sobel y-gradient image

            plt.imsave('transformation.png', sobel_filtered_image, cmap='gray')
            transformation("fourth", "-fourth_image-", "Sobel Magnitude:", "transformation.png")     # display the sobel magnitude
            
        elif event == "elim_salt_contra":  # eliminate salt noise by applying the contraharmonic mean filter  [18]

            clear_info(grayscale)
            Q = -1.5      # negative values of Q eliminates salt noise
            cv2.imwrite('transformation.png', contraharmonic(Q))
            transformation("second", "-second_image-", "Contraharmonic Mean Filter (Q="+str(Q)+"):", "transformation.png")     # display the filtered image 

        elif event == "elim_pepper_contra":   # eliminate pepper noise by applying the contraharmonic mean filter [18]  

            clear_info(grayscale)
            Q = 1.5       # postive values of Q eliminate pepper noise
            cv2.imwrite('transformation.png', contraharmonic(Q))
            transformation("second", "-second_image-", "Contraharmonic Mean Filter (Q="+str(Q)+"):", "transformation.png")     # display the filtered image 
        
        elif event == "max_filter":   # eliminate pepper noise by applying the max filter
            clear_info(grayscale)
                
            rows, columns = grayscale.shape[0], grayscale.shape[1]  # rows is the height, while columns is width
            mask = np.array([ [1, 1, 1],          # create the max filter  
                              [1, 1, 1],
                              [1, 1, 1] ])

            maxFilter = np.zeros([rows-2, columns-2])
            
            for i in range(rows-2):
                for j in range(columns-2):   # apply max filter to the input image
                    temp = np.multiply(mask, grayscale[i:i + 3, j:j + 3])
                    temp = max(temp.astype(np.uint8).flatten())     # get the max value
                    maxFilter[i, j]= temp
            
            cv2.imwrite('transformation.png', maxFilter)
            transformation("second", "-second_image-", "Max Filter:", "transformation.png")     # display the filtered image 
        
        elif event == "min_filter":   # eliminate salt noise by applying the min filter
            clear_info(grayscale)
                
            rows, columns = grayscale.shape[0], grayscale.shape[1]  # rows is the height, while columns is width
            mask = np.array([ [1, 1, 1],          # create the min filter  
                              [1, 1, 1],
                              [1, 1, 1] ])

            minFilter = np.zeros([rows-2, columns-2])
            
            for i in range(rows-2):
                for j in range(columns-2):   # apply min filter to the input image
                    temp = np.multiply(mask, grayscale[i:i + 3, j:j + 3])
                    temp = min(temp.astype(np.uint8).flatten())     # get the min value
                    minFilter[i, j]= temp
            
            cv2.imwrite('transformation.png', minFilter)
            transformation("second", "-second_image-", "Min Filter:", "transformation.png")     # display the filtered image 

        elif event == "run_length_grayscale":   # compress grayscale image through RLE [21]
            clear_info(original_grayscale)

            image_shape = np.array(original_grayscale)      # image_shape is a tuple that contains the rows and columns of the original image
            
            original_grayscale_image = np.array(original_grayscale)   
            original_grayscale_image = original_grayscale_image.reshape(original_grayscale_image.shape[0] * original_grayscale_image.shape[1])

            colorpalette, counter = np.unique(original_grayscale_image, axis=0, return_counts=True)

            grayscale_color_palette = np.uint8(np.array([val for (_, val) in sorted(zip(counter, colorpalette), key=lambda x: x[0], reverse=True)]))  # sort color palette- 
                                                                                                                                # based on most frequently used
            
            grayscale_color_palette = list(grayscale_color_palette)     # convert grayscale_color_palette into list
            original_grayscale_image = list(original_grayscale_image)   # convert original_grayscale_image into list
            

            compressed_data_grayscale = []
            i = 0
            while(i < int(len(original_grayscale_image))): # loop through pixels within the image
                
                temp_array = []
                image_pixel = original_grayscale_image[i]
                count = 1

                while(i < int(len(original_grayscale_image))-1 and count < 255 and image_pixel == original_grayscale_image[i+1]):  # group several pixels of a single value into a series
                    i = i + 1
                    count = count + 1
                
                for j in range(len(grayscale_color_palette)):      # get the palette index that represents the color value of the pixel
                    if image_pixel == grayscale_color_palette[j]:
                        palette_index = j
                        break
                
                if (count > 1 or palette_index == 0): 
                    temp_array.append(0)       # append zero (0 serves the marker for the byte-pair)
                    temp_array.append(palette_index)    # append the runvalue 
                    temp_array.append(count)        # apend the runlength 
                else:
                    temp_array.append(palette_index)    # if count is 1, append runvalue
                
                if(i < int(len(original_grayscale_image))): # proceed to next iteration
                    i = i + 1
                else:
                    break
            
                compressed_data_grayscale.extend(temp_array)
            
            compressed_data_in_bytes = (len(compressed_data_grayscale)) # compute no. of bytes of compressed data
            color_palette_in_bytes = (len(grayscale_color_palette)) # compute no. of bytes of color palette
            original_image_in_bytes = (len(original_grayscale_image)) # compute no. of bytes of original image

            total_bytes_from_compression = compressed_data_in_bytes + color_palette_in_bytes    # compute for total bytes represented compressed data

            if (total_bytes_from_compression > original_image_in_bytes):
                sg.Popup("Size of compressed image is bigger than original image. Please choose different image.", font = font, button_type = 5, title = "Error!")
            else:
                decompress_grayscale(compressed_data_grayscale, grayscale_color_palette, image_shape.shape)  # decompress the compressed image data
                
                transformation("second", "-second_image-", "Decompressed Image:", "decompressed.png")     # display the decompressed image  
                
                compression_ratio = original_image_in_bytes / total_bytes_from_compression      # compute for the compression ratio

                window["third"].update(str(original_image_in_bytes)+" bytes")     # display bytes
                window["fourth"].update(str(total_bytes_from_compression)+" bytes, CR: {:0.3f}".format((compression_ratio)))  # display compression ratio


        elif event == "run_length_rgb":   # compress RGB image through RLE
            clear_info(original_grayscale)

            if (file_name.split(".")[1] != "pcx"):

                full_image = cv2.imread("tmp.png")   # cv2.imread() returns a BGR (Blue-Green-Red) array
                RGB_image_dimensions = np.array(full_image)

                full_image = cv2.cvtColor(full_image, cv2.COLOR_RGB2BGR) # convert  BGR (Blue-Green-Red) array to RGB
                full_image = full_image.reshape(full_image.shape[0] * full_image.shape[1], 3)

                new_array = [tuple(row) for row in full_image]
                colorpalette, counter = np.unique(new_array, axis=0, return_counts=True)

                color_palette = np.uint8(np.array([val for (_, val) in sorted(zip(counter, colorpalette), key=lambda x: x[0], reverse=True)])) # sort color palette- 
                                                                                                                                            # based on most frequently used
                original_image = list(full_image)       # convert the array that represents the RGB image into a list
                for i in range(len(original_image)):                        
                    original_image[i] = list(original_image[i])
                
                original_color_palette = list(color_palette)       # convert the color palette into a list
                for i in range(len(color_palette)):
                    original_color_palette[i] = list(color_palette[i])
                
            else:
                original_image = list(RGB_full_image)       # convert the array that represents the RGB image into a list
                for i in range(len(original_image)):                        
                    original_image[i] = list(original_image[i])
            
                original_color_palette = list(RGB_color_palette)       # convert the color palette into a list
                for i in range(len(RGB_color_palette)):
                    original_color_palette[i] = list(RGB_color_palette[i])
            
            compressed_data = []      # list stores information for the compressed image
            i = 0
            while(i < int(len(original_image))):    # loop through whole image
                
                temp_array = []
                image_pixel = original_image[i]
                count = 1

                while(i < int(len(original_image))-1 and count <= 62 and image_pixel == original_image[i+1] ): # group several pixels of a single value into a series
                    i = i + 1
                    count = count + 1
                    
                for j in range(len(original_color_palette)):       # get the palette index that represents the color value of the pixel
                    if image_pixel == original_color_palette[j]:
                        palette_index = j
                        break

                if(palette_index < 192):        # palette index is less than 192
                    if count == 1:          # append palette index directly if count is one (1)
                        temp_array.append(palette_index)
                    elif count > 1:
                        temp_array.append( (np.uint8(count) + 192) ) # store as a two-byte pair representing run length and run value-
                        temp_array.append(palette_index)             # if the count is more than one (1)

                elif(192 <= palette_index < len(original_color_palette)):    # palette index is between 192 and 255
                        temp_array.append( (np.uint8(count) + 192) )    # store as a two-byte pair representing run length and run value- 
                        temp_array.append(palette_index)                # regardless of the count no.
                    
                if(i < int(len(original_image))):   # proceed to the next interation in the loop
                    i = i + 1
                else:
                    break
        
                compressed_data.extend(temp_array)     # extend temp_array to the compressed_data list
                
            compressed_data_in_bytes = ((np.array(compressed_data).flatten()).shape[0])     # compute no. of bytes of compressed data
            color_palette_in_bytes = ((np.array(original_color_palette).flatten()).shape[0])    # compute no. of bytes of color palette
            original_image_in_bytes = ((np.array(original_image).flatten()).shape[0])       # compute no. of bytes of original image

            total_bytes_from_compression = compressed_data_in_bytes + color_palette_in_bytes    # compute for total bytes represented compressed data
            
            if (total_bytes_from_compression > original_image_in_bytes):
                sg.Popup("Size of compressed image is bigger than original image. Please choose different image.", font = font, button_type = 5, title = "Error!")
            else:

                decompress_rgb(compressed_data, original_color_palette)        # decompress the compressed image data

                transformation("first", "-first_image-", "Original Image:", "tmp.png")     
                transformation("second", "-second_image-", "Decompressed Image:", "decompressed.png")     

                total_bytes_from_compression = compressed_data_in_bytes + color_palette_in_bytes        # compute for total bytes represented compressed data
                compression_ratio = original_image_in_bytes / total_bytes_from_compression      # compute for the compression ratio

                window["third"].update(str(original_image_in_bytes)+" bytes")   # display bytes
                window["fourth"].update(str(total_bytes_from_compression)+" bytes, CR: {:0.3f}".format((compression_ratio))) # display compression ratio

    window.close()