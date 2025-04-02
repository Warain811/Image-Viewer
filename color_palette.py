"""Module for handling color palette operations in the Image Viewer application."""

import os
import numpy as np
from PIL import Image

def clear_color_palette(window, current_image):
    """Clear the color palette display if current image is not in PCX format.
    
    Args:
        window: The PySimpleGUI window instance
        current_image (str): Path to the current image file
    """
    if not current_image:
        return
        
    try:
        file_ext = os.path.splitext(current_image)[1].lower()
        if file_ext != '.pcx':
            window["-colorpalette-"].update('')
    except (AttributeError, IndexError):
        # Handle invalid paths or filenames without extensions
        window["-colorpalette-"].update('')

def create_color_palette(color_data, size=(64, 64)):
    """Create a color palette image from RGB color data.
    
    Args:
        color_data (list): List of RGB color values
        size (tuple): Size of the output palette image (default: 64x64)
        
    Returns:
        PIL.Image: The generated color palette image
    """
    color_palette = Image.new('RGB', size, "black")
    pixels = color_palette.load()

    k = 0
    for i in range(0, color_palette.size[0], 4):
        for j in range(0, color_palette.size[1], 4):
            for x in range(4):
                for y in range(4):
                    pixels[i + x, j + y] = (color_data[k][0], color_data[k][1], color_data[k][2])
            k = k + 1

    return color_palette

def sort_color_palette(full_image):
    """Sort color palette based on frequency of colors in the image.
    
    Args:
        full_image (numpy.ndarray): The image data as a numpy array
        
    Returns:
        numpy.ndarray: Sorted color palette
    """
    reshaped_image = full_image.reshape(full_image.shape[0] * full_image.shape[1], 3)
    color_tuples = [tuple(row) for row in reshaped_image]
    unique_colors, counts = np.unique(color_tuples, axis=0, return_counts=True)
    
    # Sort colors by frequency (most used first)
    sorted_palette = np.uint8(np.array([
        val for (_, val) in sorted(
            zip(counts, unique_colors), 
            key=lambda x: x[0], 
            reverse=True
        )
    ]))
    
    return sorted_palette