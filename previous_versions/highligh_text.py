import fitz  # PyMuPDF
import tkinter as tk
from PIL import Image, ImageTk
import time
import io  # For in-memory byte stream

class PDFReader:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.page_number = 0  # Start at the first page
        self.page = self.doc.load_page(self.page_number)
        self.text = self.page.get_text("text")  # Extract text from the page
        self.lines = self.text.split('\n')
        self.current_sentence = 0  # Start at the first sentence

    def get_page_image(self):
        # Render the page as an image for displaying in Tkinter
        page = self.doc.load_page(self.page_number)
        pix = page.get_pixmap()
        img_data = pix.tobytes("ppm")  # Get image data as a byte string

        # Use io.BytesIO to treat img_data as a file-like object
        img_io = io.BytesIO(img_data)
        img = Image.open(img_io)  # Open the image using PIL
        return img

    def highlight_sentence(self, sentence):
        # Highlight the sentence on the PDF page
        text_instances = self.page.search_for(sentence)
        for inst in text_instances:
            highlight = self.page.add_highlight_annot(inst)
            highlight.set_colors(stroke=(1, 1, 0))  # Yellow color (RGB)
            highlight.update()

    def next_sentence(self):
        # Get the next sentence to highlight
        if self.current_sentence < len(self.lines):
            sentence = self.lines[self.current_sentence]
            self.highlight_sentence(sentence)  # Highlight the current sentence
            self.current_sentence += 1
            return True
        else:
            return False

    def save_pdf(self, output_path):
        self.doc.save(output_path)

class PDFApp:
    def __init__(self, root, pdf_reader):
        self.root = root
        self.pdf_reader = pdf_reader
        self.canvas = tk.Canvas(self.root, width=600, height=800)
        self.canvas.pack()
        self.text_label = tk.Label(self.root, text="", font=("Helvetica", 14), justify="left")
        self.text_label.pack(fill="both", expand=True)

    def update_text(self):
        lines = self.pdf_reader.lines
        self.text_label.config(text="\n".join(lines))

    def update_canvas(self):
        img = self.pdf_reader.get_page_image()  # Get the page image as PIL Image
        img_tk = ImageTk.PhotoImage(img)  # Convert to Tkinter-compatible image
        self.canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
        self.canvas.image = img_tk  # Store reference to prevent garbage collection

    def start_highlighting(self):
        try:
            while True:
                if not self.pdf_reader.next_sentence():  # If there are no more sentences, stop
                    break
                self.update_text()  # Update text display
                self.update_canvas()  # Update canvas with the latest image
                self.root.update()  # Update GUI window
                time.sleep(1.2)  # Wait for 0.5 seconds before highlighting the next sentence
        except KeyboardInterrupt:
            print("\nHighlighting stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    pdf_reader = PDFReader("pdf_files/Introduction to Information Visualization.pdf")  # Replace with your PDF path
    app = PDFApp(root, pdf_reader)
    app.start_highlighting()  # Start highlighting the PDF content
    root.mainloop()  # Keep the Tkinter window open after the process finishes
