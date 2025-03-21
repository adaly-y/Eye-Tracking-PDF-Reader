import fitz  # PyMuPDF
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # For image rendering on canvas
import io

class PDFReader:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.page_number = 0  # Start at the first page
        self.page = self.doc.load_page(self.page_number)
        self.text = self.page.get_text("text")  # Extract text from the page
        self.lines = self.text.split('\n')
        self.current_line = 0

    def get_text(self):
        # Return the text for the current page
        return self.lines

    def get_page_image(self):
        # Render the page as an image for displaying in Tkinter
        page = self.doc.load_page(self.page_number)
        pix = page.get_pixmap()
        
        # Convert the image data to bytes
        img_data = pix.tobytes("ppm")  # Export image to PPM format
        img_bytes = io.BytesIO(img_data)  # Convert to a file-like object
        
        # Open the image using PIL
        image = Image.open(img_bytes)
        return ImageTk.PhotoImage(image)  # Convert to Tkinter-compatible image

class PDFApp:
    def __init__(self, root, pdf_reader):
        self.root = root
        self.pdf_reader = pdf_reader
        self.page_number = 0
        self.current_line = 0

        # Create a frame to hold the buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.TOP, pady=10)  # Add some padding for spacing

        # Canvas for displaying PDF page as image
        self.canvas = tk.Canvas(self.root, width=600, height=800)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Label for displaying text
        self.text_label = tk.Label(self.root, text="", font=("Helvetica", 14), justify="left")
        self.text_label.pack(fill="both", expand=True)

        # Add buttons for controlling features
        self.autoscroll_button = tk.Button(button_frame, text="Start Autoscroll", command=self.toggle_autoscroll)
        self.autoscroll_button.pack(side=tk.LEFT, padx=10)

        self.highlight_button = tk.Button(button_frame, text="Start Highlighting", command=self.toggle_highlight)
        self.highlight_button.pack(side=tk.LEFT, padx=10)

        self.block_button = tk.Button(button_frame, text="Start Block Out", command=self.toggle_block)
        self.block_button.pack(side=tk.LEFT, padx=10)

        # Initialize flags for each feature
        self.autoscroll_active = False
        self.highlight_active = False
        self.block_active = False

        # Display PDF initially with no alterations
        self.update_text()
        self.update_canvas()

    def update_text(self):
        # Get the current page text
        lines = self.pdf_reader.get_text()
        self.text_label.config(text="\n".join(lines))  # Display text in the label

    def update_canvas(self):
        # Update the canvas to display the page as an image
        img = self.pdf_reader.get_page_image()
        self.canvas.create_image(0, 0, image=img, anchor=tk.NW)
        self.canvas.image = img  # Store the image reference

    def toggle_autoscroll(self):
        self.autoscroll_active = not self.autoscroll_active
        if self.autoscroll_active:
            self.highlight_active = False
            self.block_active = False
            self.start_autoscroll()

    def toggle_highlight(self):
        self.highlight_active = not self.highlight_active
        if self.highlight_active:
            self.autoscroll_active = False
            self.block_active = False
            self.highlight_current_line()

    def toggle_block(self):
        self.block_active = not self.block_active
        if self.block_active:
            self.autoscroll_active = False
            self.highlight_active = False
            self.block_non_reading_area()

    def start_autoscroll(self):
        # Autoscroll every 0.5 seconds
        if self.autoscroll_active and self.current_line < len(self.pdf_reader.lines) - 1:
            self.current_line += 1
        else:
            self.current_line = 0  # Start from the beginning when reaching the end
            self.pdf_reader.page_number += 1
            if self.pdf_reader.page_number < len(self.pdf_reader.doc):
                self.pdf_reader.page = self.pdf_reader.doc.load_page(self.pdf_reader.page_number)
                self.pdf_reader.text = self.pdf_reader.page.get_text("text")
                self.pdf_reader.lines = self.pdf_reader.text.split('\n')
            else:
                self.autoscroll_active = False  # Stop when the end of the document is reached

        if self.autoscroll_active:
            self.highlight_current_line()
            self.update_text()
            self.root.after(500, self.start_autoscroll)  # Call every 0.5 seconds

    def highlight_current_line(self):
        # Highlight the current line being read (e.g., change background color)
        highlighted_text = "\n".join(self.pdf_reader.lines[:self.current_line]) + \
                           "\n>> " + self.pdf_reader.lines[self.current_line] + " <<" + \
                           "\n".join(self.pdf_reader.lines[self.current_line + 1:])
        self.text_label.config(text=highlighted_text)

    def block_non_reading_area(self):
        # Block out non-reading areas (darken the rest of the page)
        self.canvas.create_rectangle(0, 0, 600, 800, fill="black", stipple="gray50")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Ensure the window size is sufficient
    pdf_reader = PDFReader("pdf_files/LallePaper.pdf")  # Replace with your PDF path
    app = PDFApp(root, pdf_reader)
    root.mainloop()
