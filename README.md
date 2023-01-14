# Simple Image Program 

This program for CMSC 162 opens images. It also can open 256x256 PCX images, and display their header information.
Made through Python and PySimpleGUI.

Features include:
- Transformation Options
  - Red, Green and Blue Channels
  - Grayscale 
  - Negative
  - Negative Grayscale
  - Black and Whie Threshold
  - Gamma

- Spatial Filtering Options
  - Lowpass Filters (Weighted Average, Median Square and Cross)
  - Highpass Filters (Laplacian, Unsharp Masking, Highboost Filtering)
  - Edge Detection (Sobel-Gradient)

- Noise Options
  - Salt and Pepper Noise
  - Salt Noise
  - Pepper Noise

- Image Restoration Options
  - Contraharmonic Mean Filter (Q=-1.5)
  - Contraharmonic Mean Filter (Q=1.5)
  - Min Filter
  - Max Filter

- Image Compression Options
  -  RLE for Grayscale
  -  RLE for RGB

- Least Isgnificant Bit (LSB) Watermarking
