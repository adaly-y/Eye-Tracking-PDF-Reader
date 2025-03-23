import fitz  # PyMuPDF
import time
import re

class PDFReader:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.page_number = 0  # Start at the first page
        self.page = self.doc.load_page(self.page_number)
        self.text = self.page.get_text("text")  # Extract text from the page
        self.lines = self.clean_text(self.text).split('\n')  # Cleaned and split text
        self.current_sentence = 0  # Start at the first sentence

    def clean_text(self, text):
        """
        Clean up the text by removing extra spaces, newlines, and formatting issues.
        """
        # Remove extra spaces and newlines that may affect sentence matching
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        text = text.strip()  # Remove leading/trailing whitespace
        return text

    def highlight_sentence(self, sentence):
        # Use a regular expression search to allow for slight mismatches
        sentence = sentence.strip()  # Clean the sentence before searching
        text_instances = self.page.search_for(sentence)

        # If no instances are found, skip
        if not text_instances:
            print(f"Text not found: {sentence}")
            return

        for inst in text_instances:
            # Add the highlight annotation
            highlight = self.page.add_highlight_annot(inst)  # Adds a yellow highlight
            highlight.set_colors(stroke=(1, 1, 0))  # Yellow color (RGB)
            highlight.update()

    def next_sentence(self):
        # Move to the next sentence
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
    def __init__(self, pdf_reader):
        self.pdf_reader = pdf_reader

    def start_highlighting(self, output_path):
        try:
            while True:
                if not self.pdf_reader.next_sentence():  # If there are no more sentences, stop
                    break
                time.sleep(0.5)  # Wait for 0.5 seconds before highlighting the next sentence
            # Save the modified PDF with highlights
            self.pdf_reader.save_pdf(output_path)
            print(f"PDF saved with highlights at {output_path}")
        except KeyboardInterrupt:
            print("\nHighlighting stopped.")

if __name__ == "__main__":
    pdf_reader = PDFReader("pdf_files/Introduction to Information Visualization.pdf")  # Replace with your PDF path
    app = PDFApp(pdf_reader)
    app.start_highlighting("output_highlighted.pdf")  # Output path for the highlighted PDF
