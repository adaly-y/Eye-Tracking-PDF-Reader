import tkinter as tk
from pdf_reader import PDFReader
from gui import PDFApp

if __name__ == "__main__":
    root = tk.Tk()
    pdf_reader = PDFReader("pdf_files/LallePaper.pdf")
    app = PDFApp(root, pdf_reader)
    root.mainloop()
