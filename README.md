# Image Viewer

A desktop application for viewing, transforming, and processing image files with various filters and effects.

## Features

- Open and view image files (PCX, JPEG, PNG, GIF)
- RGB channel separation
- Grayscale conversion
- Negative transformation
- Black & White transformation
- Gamma correction
- Spatial filtering effects
- Watermarking through bit-plane slicing
- Image compression (RLE)

## Project Structure

```
Image-Viewer/
├── assets/              # UI assets and icons
├── Images for Testing/  # Sample images for testing
├── src/
│   ├── core/           # Core functionality
│   │   ├── color_palette.py
│   │   ├── image_loader.py
│   │   ├── image_processor.py
│   │   └── utils.py
│   └── features/       # Feature-specific modules
│       ├── spatial_filtering.py
│       └── watermarking.py
├── tests/              # Test files
├── ui/                 # UI-related modules
│   ├── config.py
│   ├── controls.py
│   ├── image_display.py
│   └── layout.py
├── main.py            # Main application entry point
└── requirements.txt   # Project dependencies
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Image-Viewer.git
cd Image-Viewer
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Requirements

- Python 3.8+
- numpy>=1.24.0
- opencv-python>=4.8.0
- PySimpleGUI>=4.60.0
- Pillow>=10.0.0
- matplotlib>=3.7.0

## Author

John Cedric R. Warain
