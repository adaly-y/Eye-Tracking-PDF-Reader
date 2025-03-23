import pyautogui
import time

# Set the block reveal speed (seconds between revealing sentences)
block_interval = 0.5  # Adjust this value for faster/slower blocking

def block_text():
    try:
        print("Blocking text started. Switch to your PDF viewer. Press Ctrl + C to stop.")
        
        # Start blocking text
        while True:
            # Block text by simulating a masking effect (this will need to be customized based on your setup)
            pyautogui.moveTo(100, 100)  # Move mouse to the top-left of the PDF window (for blocking)
            pyautogui.mouseDown()  # Simulate mouse-down to start blocking
            pyautogui.moveTo(500, 800)  # Simulate mouse movement to cover the screen (masking)
            pyautogui.mouseUp()  # Simulate mouse-up to stop the blocking

            # Simulate revealing each sentence after 0.5 seconds
            time.sleep(block_interval)  # Wait before revealing next sentence
            pyautogui.moveTo(100, 150)  # Move to the next sentence to reveal it
            pyautogui.click()  # Simulate a click to reveal text

            # Optionally, you can use pyautogui.press("down") to move the focus to the next sentence

    except KeyboardInterrupt:
        print("\nBlocking stopped.")

if __name__ == "__main__":
    block_text()
