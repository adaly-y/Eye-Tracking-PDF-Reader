import fitz  # PyMuPDF
import tkinter as tk
from tkinter import ttk

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
        img_data = pix.tobytes()
        return img_data

class PDFApp:
    def __init__(self, root, pdf_reader):
        self.root = root
        self.pdf_reader = pdf_reader
        self.page_number = 0
        self.current_line = 0
        
        # Canvas for displaying PDF page as image
        self.canvas = tk.Canvas(self.root, width=600, height=800)
        self.canvas.pack()
        
        # Label for displaying text
        self.text_label = tk.Label(self.root, text="", font=("Helvetica", 14), justify="left")
        self.text_label.pack(fill="both", expand=True)
        
        self.update_text()
        self.autoscroll()

    def update_text(self):
        # Get the current page text
        lines = self.pdf_reader.get_text()
        # Join the lines to display in the GUI
        self.text_label.config(text="\n".join(lines))

    def autoscroll(self):
        # Autoscroll every 2 seconds
        if self.current_line < len(self.pdf_reader.lines) - 1:
            self.current_line += 1
        else:
            self.current_line = 0  # Start from the beginning when reaching the end
            self.pdf_reader.page_number += 1
            if self.pdf_reader.page_number < len(self.pdf_reader.doc):
                self.pdf_reader.page = self.pdf_reader.doc.load_page(self.pdf_reader.page_number)
                self.pdf_reader.text = self.pdf_reader.page.get_text("text")
                self.pdf_reader.lines = self.pdf_reader.text.split('\n')
            else:
                return  # End of document
        
        self.highlight_current_line()
        self.update_text()
        self.root.after(2000, self.autoscroll)  # Call every 2 seconds
    
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
    pdf_reader = PDFReader("path_to_your_pdf.pdf")  # Replace with your PDF path
    app = PDFApp(root, pdf_reader)
    root.mainloop()
