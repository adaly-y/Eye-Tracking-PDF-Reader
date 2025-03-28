import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QWidget, QMessageBox, 
                             QHBoxLayout, QSpinBox, QSlider, QTextEdit)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer

class BlockingPDFReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # PDF document attributes
        self.document = None
        self.current_page = None
        self.all_lines = []
        self.current_line_index = 0
        
        # Blocking text timer
        self.block_text_timer = QTimer(self)
        self.block_text_timer.timeout.connect(self.reveal_next_lines)

    def initUI(self):
        self.setWindowTitle('Progressive PDF Reader')
        self.setGeometry(100, 100, 1600, 900)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Top Layout for PDF and Controls
        top_layout = QHBoxLayout()
        
        # PDF Display Area
        pdf_layout = QVBoxLayout()
        self.pdf_label = QLabel('Open a PDF to begin')
        self.pdf_label.setAlignment(Qt.AlignCenter)
        pdf_layout.addWidget(self.pdf_label)
        
        # Text Display Area
        text_layout = QVBoxLayout()
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont('Arial', 14))  # Larger, more readable font
        text_layout.addWidget(self.text_display)
        
        # Controls Layout
        controls_layout = QVBoxLayout()
        
        # Open PDF Button
        open_btn = QPushButton('Open PDF')
        open_btn.clicked.connect(self.open_pdf)
        controls_layout.addWidget(open_btn)
        
        # Lines to Reveal Selector
        line_reveal_layout = QHBoxLayout()
        self.lines_selector = QSpinBox()
        self.lines_selector.setRange(1, 10)  # Allow 1-10 lines to be revealed
        self.lines_selector.setValue(1)  # Default to 1 line
        self.lines_selector.setPrefix('Reveal Lines: ')
        line_reveal_layout.addWidget(self.lines_selector)
        
        # Speed Control Slider
        self.speed_label = QLabel('Speed: Slow')
        line_reveal_layout.addWidget(self.speed_label)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1000)  # 1 second
        self.speed_slider.setMaximum(5000)  # 5 seconds
        self.speed_slider.setValue(2000)  # Default to 2 seconds
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        line_reveal_layout.addWidget(self.speed_slider)
        
        controls_layout.addLayout(line_reveal_layout)
        
        # Reveal Text Button
        reveal_text_btn = QPushButton('Reveal Text')
        reveal_text_btn.clicked.connect(self.start_revealing)
        controls_layout.addWidget(reveal_text_btn)
        
        # Reset Text Button
        reset_text_btn = QPushButton('Reset')
        reset_text_btn.clicked.connect(self.reset_text)
        controls_layout.addWidget(reset_text_btn)
        
        # Add PDF, text, and controls to top layout
        top_layout.addLayout(pdf_layout, 2)
        top_layout.addLayout(text_layout, 2)
        top_layout.addLayout(controls_layout, 1)
        
        main_layout.addLayout(top_layout)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def update_speed_label(self):
        # Update speed label based on slider value
        speed_value = self.speed_slider.value()
        if speed_value <= 1500:
            label_text = 'Speed: Very Slow'
        elif speed_value <= 2500:
            label_text = 'Speed: Slow'
        elif speed_value <= 3500:
            label_text = 'Speed: Medium'
        elif speed_value <= 4500:
            label_text = 'Speed: Fast'
        else:
            label_text = 'Speed: Very Fast'
        
        self.speed_label.setText(label_text)

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
                self.current_line_index = 0
                
                # Display full page and extract text
                self.display_page()
                self.extract_page_text()
        except Exception as e:
            # Show error message to user
            QMessageBox.critical(self, "PDF Open Error", str(e))

    def display_page(self):
        try:
            # Convert PDF page to QImage for display
            pix = self.current_page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase resolution
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

    def extract_page_text(self):
        # Extract full text of the page
        full_text = self.current_page.get_text()
        
        # Split text into lines
        self.all_lines = full_text.split('\n')
        
        # Clear previous text and reset line index
        self.text_display.clear()
        self.current_line_index = 0

    def start_revealing(self):
        # Check if a PDF is loaded
        if not self.document or not self.all_lines:
            QMessageBox.warning(self, "No Document", "Please open a PDF first.")
            return
        
        # Reset line index if we've reached the end
        if self.current_line_index >= len(self.all_lines):
            self.current_line_index = 0
        
        # Set timer interval based on slider value
        timer_interval = self.speed_slider.value()
        self.block_text_timer.start(timer_interval)

    def reveal_next_lines(self):
        # Get number of lines to reveal from spinner
        lines_to_reveal = self.lines_selector.value()
        
        # Calculate end index for revealing lines
        end_index = min(self.current_line_index + lines_to_reveal, len(self.all_lines))
        
        if self.current_line_index < len(self.all_lines):
            # Construct revealed text
            revealed_text = '\n'.join(self.all_lines[:end_index])
            
            # Update text display
            self.text_display.setPlainText(revealed_text)
            
            # Update current line index
            self.current_line_index = end_index
            
            # Stop timer if all lines revealed
            if self.current_line_index >= len(self.all_lines):
                self.block_text_timer.stop()
                QMessageBox.information(self, "Reveal Complete", "All lines have been revealed.")
        else:
            self.block_text_timer.stop()
            QMessageBox.information(self, "Reveal Complete", "All lines have been revealed.")

    def reset_text(self):
        # Check if a document is loaded
        if not self.document:
            QMessageBox.warning(self, "No Document", "Please open a PDF first.")
            return
        
        # Stop revealing timer
        if self.block_text_timer.isActive():
            self.block_text_timer.stop()
        
        # Reset current line index and clear text
        self.current_line_index = 0
        self.text_display.clear()

def main():
    app = QApplication(sys.argv)
    pdf_reader = BlockingPDFReader()
    pdf_reader.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()