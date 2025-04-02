"""
Module for handling image loading and processing functionality.
"""
import io
import os
import struct
import logging
import numpy as np
import PySimpleGUI as sg
from PIL import Image
from .color_palette import create_color_palette, sort_color_palette

def image_open(file, window):
    """Open and process an image file, with special handling for PCX format.
    
    Args:
        file (str): Path to the image file
        window: PySimpleGUI window instance
        
    Returns:
        tuple: (full_image, color_palette, image_dimensions) for PCX files
              or (None, None, None) for other formats
    """
    try:
        file_name = os.path.basename(file)
        file_ext = file_name.split(".")[1].lower()
        
        # Handle non-PCX images
        if file_ext != "pcx":
            image = Image.open(file)
            image.thumbnail((256, 256))
            bio = io.BytesIO()
            image.save(bio, "PNG")
            window["-IMAGE-"].update(data=bio.getvalue())
            get_headers_info(file, window)
            return None, None, None
            
        # Handle PCX images
        with open(file, 'rb') as f:
            # Read file bytes
            byte_data = []
            while (byte := f.read(1)):
                byte_data.append(int(struct.unpack('B', byte)[0]))

            # Extract color palette from last 768 bytes
            ColorPalette = []
            if len(byte_data) > 768:
                for i in range(len(byte_data) - 768, len(byte_data), 3):
                    ColorPalette.append([byte_data[i], byte_data[i + 1], byte_data[i + 2]])

            # Create and display color palette
            color_palette_img = create_color_palette(ColorPalette)
            color_palette_img.save("color_palette.png")
            window["-colorpalette-"].update("color_palette.png")

            # Initialize image data structures
            imageData = Image.new('RGB', (256, 256), "black")
            pixels = imageData.load()
            imageColorValues = [[0 for x in range(3)] for y in range(256 * 256)]
            paletteIndex = []
            full_image = np.zeros([256, 256, 3])

            # Process RLE encoded image data
            position = 128  # Skip header
            while position < len(byte_data) - 768:
                Byte = byte_data[position]
                position += 1

                if ((Byte & 0xC0) == 0xC0 and position < (len(byte_data) - 768)):
                    # RLE compressed pair
                    runlength = Byte & 0x3F
                    runvalue = int(byte_data[position])
                    position += 1
                else:
                    # Single pixel value
                    runlength = 1
                    runvalue = Byte

                paletteIndex.extend([runvalue] * runlength)

            # Map palette indices to RGB values
            for i in range(256 * 256):
                imageColorValues[i] = ColorPalette[paletteIndex[i]]
                y, x = divmod(i, 256)
                pixels[x, y] = tuple(imageColorValues[i])
                full_image[y][x] = imageColorValues[i]

            # Convert and save processed image
            full_image = np.array(full_image)
            image_dimensions = np.array(full_image)
            color_palette = sort_color_palette(full_image)
            
            imageData.save("tmp.png")
            window["-IMAGE-"].update("tmp.png")
            get_headers_info(file, window)

            return full_image, color_palette, image_dimensions

    except Exception as e:
        logging.error(f"Error opening image {file}: {str(e)}")
        sg.Popup(f"Error opening image: {str(e)}", title="Error")
        return None, None, None

def get_headers_info(file, window):   
    """Get and display PCX image header data.
    
    Args:
        file (str): Path to the image file
        window: PySimpleGUI window instance
    """
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

    headers_name = [    
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

    file_name = os.path.basename(file)  
    if(file_name.split(".")[1] != "pcx"):    
        window["-headerinfo-"].update("")      
        for i in range(len(headers_list)):
            window[headers_list[i]].update("")   
    else:       
        with open(f''+file, 'rb') as pcx:     
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
            pcx.seek(65)    
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

            for i in range(1, len(headers_list)):      
                window[headers_list[i]].update(headers_name[i] + headers_info_list[i])