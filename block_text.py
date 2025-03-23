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
        self.blocked_area = None  # Track the blocked area

    def get_page_image(self):
        # Render the page as an image for displaying in Tkinter
        page = self.doc.load_page(self.page_number)
        pix = page.get_pixmap()
        img_data = pix.tobytes("ppm")  # Get image data as a byte string

        # Use io.BytesIO to treat img_data as a file-like object
        img_io = io.BytesIO(img_data)
        img = Image.open(img_io)  # Open the image using PIL
        return img
    
    def block_text(self, sentence, canvas):
    # Block the area below the first sentence
    text_instances = self.page.search_for(sentence)
    for inst in text_instances:
        # Remove previous block if it exists
        if self.blocked_area:
            canvas.delete(self.blocked_area)

        # Increase the height of the block to cover a larger area
        block_height = 800  # Adjust this as needed to cover more area

        # Block the area below the first sentence
        self.blocked_area = canvas.create_rectangle(
            0, inst.y1, 600, block_height,  # Set block starting at y1 (bottom of the sentence)
            fill="black"
        )
    
    def next_sentence(self, canvas):
        # Get the next sentence to block and reveal
        if self.current_sentence < len(self.lines):
            sentence = self.lines[self.current_sentence]
            self.block_text(sentence, canvas)  # Block the current sentence
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

    def start_blocking(self):
        try:
            while True:
                if not self.pdf_reader.next_sentence(self.canvas):  # If there are no more sentences, stop
                    break
                self.update_text()  # Update text display
                self.update_canvas()  # Update canvas with the latest image
                self.root.update()  # Update GUI window
                time.sleep(1)  # Wait for 1 second before revealing the next sentence
        except KeyboardInterrupt:
            print("\nBlocking stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    pdf_reader = PDFReader("pdf_files/Introduction to Information Visualization.pdf")  # Replace with your PDF path
    app = PDFApp(root, pdf_reader)
    app.start_blocking()  # Start blocking the PDF content
    root.mainloop()  # Start Tkinter GUI loop
