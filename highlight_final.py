import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import io  # For in-memory byte stream

class PDFReader:
    def __init__(self, pdf_path):
        """
        Initialize PDF reader with the given PDF file
        
        :param pdf_path: Path to the PDF file
        """
        self.doc = fitz.open(pdf_path)
        self.page_number = 0  # Start at the first page
        self.page = self.doc.load_page(self.page_number)
        self.lines = self.page.get_text("text").split('\n')
        self.current_sentence = 0  # Start at the first sentence

    def get_page_with_highlights(self):
        """
        Render the current page with existing highlights
        
        :return: PIL Image of the page
        """
        page = self.doc.load_page(self.page_number)
        pix = page.get_pixmap()
        img_data = pix.tobytes("ppm")  # Get image data as a byte string

        # Use io.BytesIO to treat img_data as a file-like object
        img_io = io.BytesIO(img_data)
        img = Image.open(img_io)  # Open the image using PIL
        return img

    def highlight_sentence(self, sentence):
        """
        Highlight a specific sentence on the PDF page with bright yellow
        
        :param sentence: Sentence to highlight
        """
        # Search for the sentence on the page
        text_instances = self.page.search_for(sentence)
        
        # If no text found, try partial matching
        if not text_instances:
            # Try finding partial matches
            for line in self.lines:
                if sentence.strip() in line.strip():
                    text_instances = self.page.search_for(line)
                    break
        
        # Add highlights for each text instance found
        for inst in text_instances:
            # Use bright yellow color for stroke/border
            highlight = self.page.add_highlight_annot(inst)
            highlight.set_colors(stroke=(1, 1, 0))  # Bright yellow border
            highlight.update()

    def next_sentences(self, num_lines):
        """
        Highlight the next specified number of lines
        
        :param num_lines: Number of lines to highlight
        :return: True if lines were highlighted, False if no more lines
        """
        lines_highlighted = 0
        while lines_highlighted < num_lines and self.current_sentence < len(self.lines):
            sentence = self.lines[self.current_sentence]
            self.highlight_sentence(sentence)
            self.current_sentence += 1
            lines_highlighted += 1
        
        return lines_highlighted > 0

    def save_pdf(self, output_path):
        """
        Save the modified PDF
        
        :param output_path: Path to save the highlighted PDF
        """
        self.doc.save(output_path)

class PDFHighlighterApp:
    def __init__(self, root):
        """
        Initialize the PDF Highlighter Application
        
        :param root: Tkinter root window
        """
        self.root = root
        self.root.title("PDF Sentence Highlighter")
        self.pdf_reader = None
        self.is_highlighting = False
        
        # Configure root window to expand
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create UI elements
        self.create_ui()

    def create_ui(self):
        """
        Create the user interface for the PDF Highlighter
        """
        # Top Control Frame
        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        top_frame.grid_columnconfigure(4, weight=1)

        # PDF Selection Button
        self.select_pdf_btn = tk.Button(
            top_frame, 
            text="Select PDF", 
            command=self.select_pdf
        )
        self.select_pdf_btn.grid(row=0, column=0, padx=5)

        # Lines to Highlight Input
        tk.Label(top_frame, text="Lines per Iteration:").grid(row=0, column=1, padx=2)
        self.lines_entry = tk.Entry(top_frame, width=5)
        self.lines_entry.grid(row=0, column=2, padx=5)
        self.lines_entry.insert(0, "1")  # Default to 1 line

        # Delay Input
        tk.Label(top_frame, text="Delay (seconds):").grid(row=0, column=3, padx=0)
        self.delay_entry = tk.Entry(top_frame, width=5)
        self.delay_entry.grid(row=0, column=4, padx=5)
        self.delay_entry.insert(0, "1.2")  # Default delay

        # Start/Stop Highlighting Button
        self.highlight_btn = tk.Button(
            top_frame, 
            text="Start Highlighting", 
            command=self.toggle_highlighting,
            state=tk.DISABLED
        )
        self.highlight_btn.grid(row=0, column=5, padx=5)

        # Save PDF Button
        self.save_btn = tk.Button(
            top_frame, 
            text="Save Highlighted PDF", 
            command=self.save_pdf,
            state=tk.DISABLED
        )
        self.save_btn.grid(row=0, column=6, padx=5)

        # Canvas for PDF Preview
        self.canvas = tk.Canvas(self.root, width=600, height=800)
        self.canvas.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

    def select_pdf(self):
        """
        Open file dialog to select a PDF
        """
        pdf_path = filedialog.askopenfilename(
            title="Select PDF File", 
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if pdf_path:
            try:
                self.pdf_reader = PDFReader(pdf_path)
                self.update_canvas()
                self.highlight_btn.config(state=tk.NORMAL)
                self.save_btn.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF: {str(e)}")

    def update_canvas(self):
        """
        Update the canvas with the current PDF page image
        """
        img = self.pdf_reader.get_page_with_highlights()
        img_tk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
        self.canvas.image = img_tk  # Store reference to prevent garbage collection

    def toggle_highlighting(self):
        """
        Toggle highlighting on and off
        """
        if not self.is_highlighting:
            # Start highlighting
            try:
                # Get user inputs
                lines_per_iteration = int(self.lines_entry.get())
                delay = float(self.delay_entry.get())

                # Disable inputs during highlighting
                self.lines_entry.config(state=tk.DISABLED)
                self.delay_entry.config(state=tk.DISABLED)
                self.select_pdf_btn.config(state=tk.DISABLED)
                
                # Change button text
                self.highlight_btn.config(text="Stop Highlighting")
                
                # Set highlighting flag
                self.is_highlighting = True
                
                # Start highlighting
                self.highlight_with_delay(lines_per_iteration, delay)

            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter valid numbers.")
        else:
            # Stop highlighting
            self.is_highlighting = False
            
            # Re-enable inputs
            self.lines_entry.config(state=tk.NORMAL)
            self.delay_entry.config(state=tk.NORMAL)
            self.select_pdf_btn.config(state=tk.NORMAL)
            
            # Reset button text
            self.highlight_btn.config(text="Start Highlighting")

    def highlight_with_delay(self, lines_per_iteration, delay):
        """
        Highlight sentences with specified number of lines and delay
        
        :param lines_per_iteration: Number of lines to highlight in each iteration
        :param delay: Delay between iterations in seconds
        """
        # Check if highlighting should continue
        if not self.is_highlighting:
            return

        if self.pdf_reader.next_sentences(lines_per_iteration):
            self.update_canvas()
            
            # Schedule next highlighting iteration
            self.root.after(int(delay * 1000), 
                            lambda: self.highlight_with_delay(lines_per_iteration, delay))
        else:
            # Highlighting complete
            self.toggle_highlighting()
            messagebox.showinfo("Complete", "PDF highlighting finished!")

    def save_pdf(self):
        """
        Save the highlighted PDF to a user-selected location
        """
        if self.pdf_reader:
            output_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )
            if output_path:
                try:
                    self.pdf_reader.save_pdf(output_path)
                    messagebox.showinfo("Success", f"PDF saved to {output_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save PDF: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No PDF loaded.")

def main():
    root = tk.Tk()
    root.geometry("800x900")  # Set a default window size
    app = PDFHighlighterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()