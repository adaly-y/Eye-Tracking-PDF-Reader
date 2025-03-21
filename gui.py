import tkinter as tk
from pdf_reader import PDFReader
from features import toggle_autoscroll, toggle_highlight, toggle_block

class PDFApp:
    def __init__(self, root, pdf_reader):
        self.root = root
        self.pdf_reader = pdf_reader
        self.page_number = 0
        self.current_line = 0
        self.setup_gui()

    def setup_gui(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.TOP, pady=10)
        
        self.canvas = tk.Canvas(self.root, width=600, height=800)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.text_label = tk.Label(self.root, text="", font=("Helvetica", 14), justify="left")
        self.text_label.pack(fill="both", expand=True)
        
        # Adding buttons
        self.autoscroll_button = tk.Button(button_frame, text="Start Autoscroll", command=self.toggle_autoscroll)
        self.autoscroll_button.pack(side=tk.LEFT, padx=10)
        
        self.highlight_button = tk.Button(button_frame, text="Start Highlighting", command=self.toggle_highlight)
        self.highlight_button.pack(side=tk.LEFT, padx=10)
        
        self.block_button = tk.Button(button_frame, text="Start Block Out", command=self.toggle_block)
        self.block_button.pack(side=tk.LEFT, padx=10)
    
    def toggle_autoscroll(self):
        toggle_autoscroll(self)

    def toggle_highlight(self):
        toggle_highlight(self)

    def toggle_block(self):
        toggle_block(self)
