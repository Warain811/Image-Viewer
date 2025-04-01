import PySimpleGUI as sg
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import numpy as np
import os

class ImageDisplayManager:
    """Handles image display and transformations in the UI"""
    
    def __init__(self, window):
        self.window = window

    def display_transformation(self, transform_name, transform_image, transformation):
        """Display transformed image in window with specified parameters.
        
        Args:
            transform_name: Key for transformation text
            transform_image: Key for image display element
            transformation: Description text to display
        """
        image = Image.open("transformation.png")
        image.thumbnail((256, 256))
        self.window[transform_name].update(transformation)   
        self.window[transform_image].update(data=ImageTk.PhotoImage(image))

    def display_histogram(self, image):
        """Generate and display histogram for image.
        
        Args:
            image: Input image array
        """
        plt.ticklabel_format(style='plain')
        vals = image.sum(axis=2).flatten()
        counts, bins = np.histogram(vals, range(257))
        plt.bar(bins[:-1] - 0.5, counts, width=1, edgecolor='none')
        plt.xlim([-2, 255.5])
        plt.savefig('histogram.png', bbox_inches='tight', dpi=60)
        plt.close()

        self.window["-histogram-"].update("Histogram:")   
        self.window["-HISTOGRAM-"].update("histogram.png")
        
        # Cleanup temporary file
        os.remove("histogram.png")