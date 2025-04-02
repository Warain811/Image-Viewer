import PySimpleGUI as sg

class UIControls:
    """Manages UI control elements like sliders and buttons"""
    
    def __init__(self, window):
        """Initialize with window reference.
        
        Args:
            window: PySimpleGUI window instance
        """
        self.window = window

    def show_slider(self, slider_value):
        """Show slider and related controls.
        
        Args:
            slider_value (int): Maximum value for slider range
        """
        # Show navigation buttons
        self.window["left"].update(visible=True)
        self.window["right"].update(visible=True)
        
        # Show slider with range
        self.window["-slider-"].update(
            visible=True, 
            range=(0, slider_value)
        )
        
        # Show threshold controls  
        self.window["Apply"].update(visible=True)
        self.window["threshold"].update(visible=True)
        self.window["threshold_value"].update(visible=True)