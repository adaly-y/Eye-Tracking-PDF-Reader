import pyautogui
import time

# Set the scroll speed (seconds between scrolls)
scroll_interval = 0.2  # Adjust this value for faster/slower scrolling

try:
    print("Auto-scrolling started. Switch to your PDF viewer. Press Ctrl + C to stop.")
    
    while True:
        pyautogui.press("down")  # Simulates pressing the "Down Arrow" key
        time.sleep(scroll_interval)  # Wait before scrolling again

except KeyboardInterrupt:
    print("\nAuto-scrolling stopped.")
