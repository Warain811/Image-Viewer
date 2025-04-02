"""
Module for functions that process and transform images.
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

# Function to apply grayscale transformation
def apply_grayscale(image_path, output_path="transformation.png"):
    image = cv2.imread(image_path)
    r, g, b = image[:, :, 2], image[:, :, 1], image[:, :, 0]
    gray = np.uint8(0.2989 * r + 0.5870 * g + 0.1140 * b)
    cv2.imwrite(output_path, gray)
    return gray

# Function to apply negative transformation
def apply_negative(image_path, output_path="transformation.png"):
    image = cv2.imread(image_path)
    negative = abs(255 - image[:, :, :])
    cv2.imwrite(output_path, negative)
    return negative

# Function to generate and save histogram
def generate_histogram(image, output_path="histogram.png"):
    plt.ticklabel_format(style='plain')
    vals = image.sum(axis=2).flatten()
    counts, bins = np.histogram(vals, range(257))
    plt.bar(bins[:-1] - 0.5, counts, width=1, edgecolor='none')
    plt.xlim([-2, 255.5])
    plt.savefig(output_path, bbox_inches='tight', dpi=60)
    plt.close()
