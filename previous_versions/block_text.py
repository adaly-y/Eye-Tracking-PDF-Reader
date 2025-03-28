import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QWidget, QMessageBox, 
                             QHBoxLayout, QSpinBox)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

class BlockingPDFReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # PDF document attributes
        self.document = None
        self.current_page = None
        self.lines = []
        self.current_line_index = 0
        
        # Blocking text timer
        self.block_text_timer = QTimer(self)
        self.block_text_timer.timeout.connect(self.reveal_next_lines)

    def initUI(self):
        self.setWindowTitle('Blocking PDF Reader')
        self.setGeometry(100, 100, 1000, 800)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # PDF Display Area
        self.pdf_label = QLabel('Open a PDF to begin')
        self.pdf_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.pdf_label)
        
        # Controls Layout
        controls_layout = QHBoxLayout()
        
        # Open PDF Button
        open_btn = QPushButton('Open PDF')
        open_btn.clicked.connect(self.open_pdf)
        controls_layout.addWidget(open_btn)
        
        # Lines to Reveal Selector
        self.lines_selector = QSpinBox()
        self.lines_selector.setRange(1, 10)  # Allow 1-10 lines to be revealed
        self.lines_selector.setValue(1)  # Default to 1 line
        self.lines_selector.setPrefix('Reveal Lines: ')
        controls_layout.addWidget(self.lines_selector)
        
        # Block Text Button
        block_text_btn = QPushButton('Block Text')
        block_text_btn.clicked.connect(self.start_block_text)
        controls_layout.addWidget(block_text_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Text Display Area
        self.text_label = QLabel('')
        self.text_label.setWordWrap(True)
        main_layout.addWidget(self.text_label)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def open_pdf(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, 'Open PDF', '', 'PDF Files (*.pdf)')
            if file_path:
                # Open the document
                self.document = fitz.open(file_path)
                
                # Verify document is not empty
                if len(self.document) == 0:
                    raise ValueError("The PDF document is empty")
                
                self.current_page = self.document[0]
                self.display_page()
                self.extract_lines()
        except Exception as e:
            # Show error message to user
            QMessageBox.critical(self, "PDF Open Error", str(e))

    def display_page(self):
        try:
            # Convert PDF page to QImage for display
            pix = self.current_page.get_pixmap()
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            
            # Convert QImage to QPixmap
            pixmap = QPixmap.fromImage(img)
            scaled_pixmap = pixmap.scaled(self.pdf_label.size(), 
                                          Qt.KeepAspectRatio, 
                                          Qt.SmoothTransformation)
            
            self.pdf_label.setPixmap(scaled_pixmap)
        except Exception as e:
            # Error handling for page display
            QMessageBox.warning(self, "Display Error", str(e))

    def extract_lines(self):
        try:
            # Extract text and split into lines
            text = self.current_page.get_text()
            
            # Split text into lines, removing empty lines
            self.lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Print lines to console for verification
            print(f"Extracted {len(self.lines)} lines")
            for i, line in enumerate(self.lines[:5], 1):
                print(f"Line {i}: {line}")
        except Exception as e:
            print(f"Error extracting lines: {str(e)}")
            self.lines = []

    def start_block_text(self):
        # Check if lines have been extracted
        if not self.lines:
            QMessageBox.warning(self, "No Lines", "Please open a PDF first and ensure it contains text.")
            return
        
        # Reset line index and start blocking
        self.current_line_index = 0
        self.text_label.setText('')  # Clear previous text
        self.block_text_timer.start(1000)  # 1-second delay

    def reveal_next_lines(self):
        # Get number of lines to reveal from spinner
        lines_to_reveal = self.lines_selector.value()
        
        # Calculate end index for revealing lines
        end_index = min(self.current_line_index + lines_to_reveal, len(self.lines))
        
        if self.current_line_index < len(self.lines):
            # Reveal lines
            revealed_lines = '\n'.join(self.lines[self.current_line_index:end_index])
            self.text_label.setText(revealed_lines)
            
            # Update current line index
            self.current_line_index = end_index
            
            # Stop timer if all lines revealed
            if self.current_line_index >= len(self.lines):
                self.block_text_timer.stop()
                QMessageBox.information(self, "Blocking Complete", "All lines have been revealed.")
        else:
            self.block_text_timer.stop()
            QMessageBox.information(self, "Blocking Complete", "All lines have been revealed.")

def main():
    app = QApplication(sys.argv)
    pdf_reader = BlockingPDFReader()
    pdf_reader.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()