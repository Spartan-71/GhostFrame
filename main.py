import cv2
import numpy as np
import pygetwindow as gw
from PIL import ImageGrab
import time
import tkinter as tk
from tkinter import ttk, filedialog
import threading
import os
from datetime import datetime

class ModernScreenRecorder:
    def __init__(self):
        self.recording = False
        self.paused = False
        self.output = None
        self.selected_window = None
        self.thread = None
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("Screen Recorder")
        self.root.geometry("350x600")
        self.root.resizable(True, True)
        
        # Set theme
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Status.TLabel', font=('Helvetica', 10))
        style.configure('Action.TButton', font=('Helvetica', 10, 'bold'))
        
        # Create main container with padding
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            self.main_container,
            text="Screen Recorder",
            style='Header.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Create sections
        self.create_window_selection_section()
        self.create_save_location_section()
        self.create_recording_options_section()
        self.create_controls_section()
        self.create_status_section()
        
        # Initialize path variables
        self.default_directory = os.path.expanduser("~/Videos")
        if not os.path.exists(self.default_directory):
            self.default_directory = os.path.expanduser("~/Documents")
        
        # Set initial save path
        self.update_save_path()
    
    def create_window_selection_section(self):
        """Create the window selection section"""
        section = ttk.LabelFrame(
            self.main_container,
            text="Window Selection",
            padding="10"
        )
        section.pack(fill=tk.X, pady=(0, 10))
        
        # Window dropdown
        self.window_var = tk.StringVar()
        self.window_dropdown = ttk.Combobox(
            section,
            textvariable=self.window_var,
            state="readonly",
            height=15
        )
        self.window_dropdown.pack(fill=tk.X, pady=(0, 5))
        
        # Refresh button
        refresh_btn = ttk.Button(
            section,
            text="↻ Refresh Window List",
            command=self.update_window_list,
            style='Action.TButton'
        )
        refresh_btn.pack(fill=tk.X)
        
        self.update_window_list()
    
    def create_save_location_section(self):
        """Create the save location section"""
        section = ttk.LabelFrame(
            self.main_container,
            text="Save Location",
            padding="10"
        )
        section.pack(fill=tk.X, pady=(0, 10))
        
        # Directory selection
        dir_frame = ttk.Frame(section)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        dir_label = ttk.Label(dir_frame, text="Directory:")
        dir_label.pack(side=tk.LEFT)
        
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_btn = ttk.Button(
            dir_frame,
            text="Browse",
            command=self.browse_directory
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Filename configuration
        file_frame = ttk.Frame(section)
        file_frame.pack(fill=tk.X)
        
        file_label = ttk.Label(file_frame, text="Filename:")
        file_label.pack(side=tk.LEFT)
        
        self.filename_var = tk.StringVar()
        self.filename_entry = ttk.Entry(file_frame, textvariable=self.filename_var)
        self.filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        extension_label = ttk.Label(file_frame, text=".avi")
        extension_label.pack(side=tk.RIGHT)
    
    def create_recording_options_section(self):
        """Create the recording options section"""
        section = ttk.LabelFrame(
            self.main_container,
            text="Recording Options",
            padding="10"
        )
        section.pack(fill=tk.X, pady=(0, 10))
        
        # FPS selection
        fps_frame = ttk.Frame(section)
        fps_frame.pack(fill=tk.X, pady=(0, 5))
        
        fps_label = ttk.Label(fps_frame, text="FPS:")
        fps_label.pack(side=tk.LEFT)
        
        self.fps_var = tk.StringVar(value="30")
        fps_values = ["15", "30", "60"]
        fps_combo = ttk.Combobox(
            fps_frame,
            textvariable=self.fps_var,
            values=fps_values,
            state="readonly",
            width=10
        )
        fps_combo.pack(side=tk.LEFT, padx=5)
    
    def create_controls_section(self):
        """Create the controls section"""
        section = ttk.LabelFrame(
            self.main_container,
            text="Controls",
            padding="10"
        )
        section.pack(fill=tk.X, pady=(0, 10))
        
        # Control buttons
        self.start_button = ttk.Button(
            section,
            text="▶ Start Recording",
            command=self.start_recording,
            style='Action.TButton'
        )
        self.start_button.pack(fill=tk.X, pady=(0, 5))
        
        self.pause_button = ttk.Button(
            section,
            text="⏸ Pause",
            command=self.pause_recording,
            state="disabled",
            style='Action.TButton'
        )
        self.pause_button.pack(fill=tk.X, pady=(0, 5))
        
        self.stop_button = ttk.Button(
            section,
            text="⏹ Stop Recording",
            command=self.stop_recording,
            state="disabled",
            style='Action.TButton'
        )
        self.stop_button.pack(fill=tk.X)
    
    def create_status_section(self):
        """Create the status section"""
        section = ttk.LabelFrame(
            self.main_container,
            text="Status",
            padding="10"
        )
        section.pack(fill=tk.X)
        
        self.status_label = ttk.Label(
            section,
            text="Ready to record",
            style='Status.TLabel'
        )
        self.status_label.pack()
        
        self.time_label = ttk.Label(
            section,
            text="00:00:00",
            style='Header.TLabel'
        )
        self.time_label.pack(pady=(5, 0))
    
    def update_save_path(self):
        """Update the save path with current values"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.dir_var.set(self.default_directory)
        self.filename_var.set(f"recording_{timestamp}")
    
    def browse_directory(self):
        """Open directory selection dialog"""
        directory = filedialog.askdirectory(
            initialdir=self.dir_var.get(),
            title="Select Save Directory"
        )
        if directory:
            self.dir_var.set(directory)
    
    def get_save_path(self):
        """Get the complete save path"""
        directory = self.dir_var.get()
        filename = self.filename_var.get()
        return os.path.join(directory, f"{filename}.avi")
    
    def update_window_list(self):
        """Update the list of available windows"""
        windows = gw.getAllWindows()
        # Filter out minimized windows and windows with empty titles
        window_titles = [w.title for w in windows if w.title.strip() and not w.isMinimized]
        self.window_dropdown['values'] = sorted(window_titles)
        if window_titles:
            self.window_dropdown.set(window_titles[0])
        
    def get_window_coordinates(self):
        """Get the coordinates of the selected window"""
        window_title = self.window_var.get()
        try:
            window = gw.getWindowsWithTitle(window_title)[0]
            # Check if window is visible and not minimized
            if window.isMinimized:
                self.status_label['text'] = "Error: Selected window is minimized"
                return None
                
            # Get the window boundaries including borders and title bar
            # Add small padding to ensure we capture the full window
            left = window.left
            top = window.top
            width = window.width
            height = window.height
            
            # Adjust for Windows DPI scaling
            try:
                import ctypes
                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
            except:
                pass
                
            # Ensure we're not going beyond screen boundaries
            screen_width = user32.GetSystemMetrics(0) if 'user32' in locals() else 1920
            screen_height = user32.GetSystemMetrics(1) if 'user32' in locals() else 1080
            
            # Adjust coordinates to stay within screen bounds
            left = max(0, left)
            top = max(0, top)
            width = min(width, screen_width - left)
            height = min(height, screen_height - top)
            
            # Ensure minimum dimensions
            width = max(1, width)
            height = max(1, height)
            
            return {
                'left': left,
                'top': top,
                'width': width,
                'height': height
            }
        except IndexError:
            self.status_label['text'] = "Error: Window not found"
            return None
        except Exception as e:
            self.status_label['text'] = f"Error: {str(e)}"
            return None

    def record_screen(self):
        """Record the screen"""
        initial_coords = self.get_window_coordinates()
        if not initial_coords:
            self.status_label['text'] = "Error: Window not found"
            self.stop_recording()
            return
        
        # Initialize video writer
        fps = float(self.fps_var.get())
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        
        try:
            self.output = cv2.VideoWriter(
                self.get_save_path(),
                fourcc,
                fps,
                (initial_coords['width'], initial_coords['height'])
            )
        except Exception as e:
            self.status_label['text'] = f"Error: Could not create output file - {str(e)}"
            self.stop_recording()
            return

        # Start time counter
        time_thread = threading.Thread(target=self.update_recording_time)
        time_thread.daemon = True
        time_thread.start()
        
        while self.recording:
            if not self.paused:
                try:
                    # Get current coordinates
                    coords = self.get_window_coordinates()
                    if not coords:
                        continue
                    
                    # Capture the screen
                    screenshot = ImageGrab.grab(bbox=(
                        coords['left'],
                        coords['top'],
                        coords['left'] + coords['width'],
                        coords['top'] + coords['height']
                    ))
                    
                    # Resize if window dimensions changed
                    if (screenshot.size[0] != initial_coords['width'] or 
                        screenshot.size[1] != initial_coords['height']):
                        screenshot = screenshot.resize((
                            initial_coords['width'],
                            initial_coords['height']
                        ))
                    
                    # Convert and write frame
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    self.output.write(frame)
                    
                except Exception as e:
                    self.status_label['text'] = f"Recording error: {str(e)}"
                    continue
                    
            time.sleep(1/fps)
    
    def update_recording_time(self):
        """Update the recording time display"""
        start_time = time.time()
        while self.recording:
            if not self.paused:
                elapsed = int(time.time() - start_time)
                hours = elapsed // 3600
                minutes = (elapsed % 3600) // 60
                seconds = elapsed % 60
                self.time_label['text'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            time.sleep(1)
    
    
    def start_recording(self):
        """Start recording"""
        save_path = self.get_save_path()
        save_dir = os.path.dirname(save_path)
        
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except Exception as e:
                self.status_label['text'] = "Error: Could not create directory"
                return
        
        self.recording = True
        self.paused = False
        self.thread = threading.Thread(target=self.record_screen)
        self.thread.daemon = True
        self.thread.start()
        
        self.start_button['state'] = 'disabled'
        self.pause_button['state'] = 'normal'
        self.stop_button['state'] = 'normal'
        self.window_dropdown['state'] = 'disabled'
        self.status_label['text'] = "Recording..."
    
    def pause_recording(self):
        """Pause/Resume recording"""
        self.paused = not self.paused
        self.pause_button['text'] = "▶ Resume" if self.paused else "⏸ Pause"
        self.status_label['text'] = "Paused" if self.paused else "Recording..."
    
    def stop_recording(self):
        """Stop recording"""
        self.recording = False
        if self.thread:
            self.thread.join()
        if self.output:
            self.output.release()
        
        self.start_button['state'] = 'normal'
        self.pause_button['state'] = 'disabled'
        self.stop_button['state'] = 'disabled'
        self.window_dropdown['state'] = 'readonly'
        self.status_label['text'] = "Ready to record"
        self.pause_button['text'] = "⏸ Pause"
        self.time_label['text'] = "00:00:00"
        
        # Update filename for next recording
        self.update_save_path()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernScreenRecorder()
    app.run()