import cv2
import numpy as np
import pyautogui
import time
import keyboard  # For detecting key presses

def record_screen(output="screen_recording.avi", duration=10, fps=30):
    screen_size = pyautogui.size()
    codec = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output, codec, fps, screen_size)

    print(f"Recording for {duration} seconds... Press 'q' to stop early.")

    start_time = time.time()
    end_time = start_time + duration
    frame_time = 1 / fps  # Time between frames in seconds

    while True:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame)

        # Check if the time limit has been reached or if 'q' is pressed
        if time.time() >= end_time:
            print("Stopping recording...")
            break
        
        # Sleep to maintain the desired frame rate
        time.sleep(frame_time)

    out.release()
    print(f"Recording saved as {output}")

# User can specify the duration in seconds
if __name__ == "__main__":
    duration = int(input("Enter duration in seconds for screen recording: "))
    record_screen(duration=duration)
