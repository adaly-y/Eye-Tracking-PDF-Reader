import fitz  # PyMuPDF

class PDFReader:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.page_number = 0
        self.page = self.doc.load_page(self.page_number)
        self.text = self.page.get_text("text")
        self.lines = self.text.split('\n')
        self.current_line = 0

    def get_text(self):
        return self.lines

    def get_page_image(self):
        # Handle image rendering logic here...
        page = self.doc.load_page(self.page_number)
        pix = page.get_pixmap()
        img_data = pix.tobytes("ppm")
        return img_data
