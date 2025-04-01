import PySimpleGUI as sg
from ui.config import UI_TEXT_COLOR, UI_INPUT_TEXT_COLOR

def create_file_column():
    """Create the file operations column layout"""
    return [     # left column of the program
      [
          sg.Text("File Name:", text_color = UI_TEXT_COLOR),       # text element
          sg.Input(size=(26, 1), disabled = True, text_color = UI_INPUT_TEXT_COLOR, key="-FILE-"),    # input element with key 'FILE'
          sg.Button('Browse'),        # 'browse' button element
          sg.Button("Load Image"),    # 'load image' button element 
      ],

      [
          sg.Text("Load History:", size = (60, 1), text_color = UI_TEXT_COLOR, justification='center')   # text element  
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

      [sg.Text("Transformation Options:", size = (60, 1), text_color = UI_TEXT_COLOR, justification='center'), ], # text element
      
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

def create_image_viewer_column():
    """Create the image viewer column layout"""
    return [     # right column of the program
      [sg.Text("View of the image:", text_color = UI_TEXT_COLOR, justification = 'center')],     # text elements
      [
          sg.Image(key="-IMAGE-", size = (320, 240), filename="empty.png"),   # image elements
          sg.Image(key="-colorpalette-", size = (90, 90)),                  
      ], 
      [sg.Text("")],      
      [sg.Text(size=(30, 1), key="-headerinfo-", text_color = UI_TEXT_COLOR, justification = 'center')],   # these text elements-
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

def create_transformation_column():
    """Create the transformation column layout"""
    return [
        [sg.Text(size=(45, 1), key="-transformation-", text_color = UI_TEXT_COLOR, justification = 'center')],   # elements from 217-229  
        [sg.Image(key="-TRANSFORMATION-", size = (320, 240))],                                              # are for image transforming
        [
            sg.Input(size=(5, 1), text_color = UI_INPUT_TEXT_COLOR, key="threshold_value", disabled=True),  
            sg.Text("", key = "threshold", text_color = UI_TEXT_COLOR),
        ],    

        [
            sg.Slider(range = (0, 255), key='-slider-', orientation='h', enable_events=True, disable_number_display= True, resolution = False),
            sg.Button(key='left', image_filename = "left_arrow.png", pad = ((2, 0), (3, 0))),
            sg.Button(key='right', image_filename = "right_arrow.png", pad = ((3, 0), (3, 0))),
            sg.Button('Apply', key='Apply', pad = ((10, 0), (10, 0))),        
        ],

        [sg.Text(size=(30, 1), key="-histogram-", text_color = UI_TEXT_COLOR, justification = 'center')],   # text element
        [sg.Image(key="-HISTOGRAM-")], # image element for the histogram
    ]

def create_layout():
    """Create the main window layout"""
    return [
        [
            sg.Column(create_file_column(), vertical_alignment='center', p=((0, 3), (60, 75))),
            sg.VSeperator(),
            sg.Column(create_image_viewer_column(), element_justification="center", expand_y=True),
            sg.VSeperator(),
            sg.Column(create_transformation_column(), element_justification="center", expand_y=True),
        ]
    ]