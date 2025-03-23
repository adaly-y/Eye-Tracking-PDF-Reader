# gui.py
import tkinter as tk
from pdf_reader import PDFReader
from features import toggle_autoscroll, toggle_highlight, toggle_block

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
        toggle_autoscroll(self)

    def toggle_highlight(self):
        toggle_highlight(self)

    def toggle_block(self):
        toggle_block(self)
