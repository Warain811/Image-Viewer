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

    def update_slider(self, value):
        """Update slider and threshold value with validation.
        
        Args:
            value: New slider value to set
            
        Returns:
            float: The rounded and clamped value that was set, or None if validation failed
        """
        # Convert and validate numeric value 
        try:
            value = float(value)
            if not isinstance(value, (int, float)):
                return None
        except (ValueError, TypeError):
            return None
            
        # Round and clamp value based on slider range
        min_val = 0
        max_val = self.window['-slider-'].Range[1] or 255
        rounded = round(min(max(value, min_val), max_val), 1)
        
        # Update UI elements atomically
        self.window.write_event_value('-update-ui-', {
            '-slider-': rounded,
            'threshold_value': rounded
        })
        
        # Refresh display
        self.window['-slider-'].update(rounded)
        self.window['threshold_value'].update(rounded)
        
        return rounded