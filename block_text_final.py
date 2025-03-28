import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QWidget, QMessageBox, 
                             QHBoxLayout, QSpinBox, QSlider, QTextEdit)
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
        self.revealed_text = ""
        
        # Blocking text timer
        self.block_text_timer = QTimer(self)
        self.block_text_timer.timeout.connect(self.reveal_next_lines)

    def initUI(self):
        self.setWindowTitle('Blocking PDF Reader')
        self.setGeometry(100, 100, 1200, 800)
        
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
        
        # Block Text Button
        block_text_btn = QPushButton('Block Text')
        block_text_btn.clicked.connect(self.start_block_text)
        controls_layout.addWidget(block_text_btn)
        
        # Clear Text Button
        clear_text_btn = QPushButton('Clear Text')
        clear_text_btn.clicked.connect(self.clear_text)
        controls_layout.addWidget(clear_text_btn)
        
        # Add PDF and controls to top layout
        top_layout.addLayout(pdf_layout, 1)
        top_layout.addLayout(controls_layout, 1)
        
        main_layout.addLayout(top_layout)
        
        # Text Display Area (now a QTextEdit for better text management)
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        main_layout.addWidget(self.text_display)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def clear_text(self):
        # Clear the revealed text and reset line index
        self.revealed_text = ""
        self.current_line_index = 0
        self.text_display.clear()
        
        # Stop the timer if it's running
        if self.block_text_timer.isActive():
            self.block_text_timer.stop()

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
        
        # Reset line index if we've reached the end
        if self.current_line_index >= len(self.lines):
            self.current_line_index = 0
        
        # Set timer interval based on slider value
        timer_interval = self.speed_slider.value()
        self.block_text_timer.start(timer_interval)

    def reveal_next_lines(self):
        # Get number of lines to reveal from spinner
        lines_to_reveal = self.lines_selector.value()
        
        # Calculate end index for revealing lines
        end_index = min(self.current_line_index + lines_to_reveal, len(self.lines))
        
        if self.current_line_index < len(self.lines):
            # Reveal lines
            revealed_lines = '\n'.join(self.lines[self.current_line_index:end_index])
            
            # Append revealed lines to existing text
            if self.revealed_text:
                self.revealed_text += '\n' + revealed_lines
            else:
                self.revealed_text = revealed_lines
            
            # Update text display
            self.text_display.setText(self.revealed_text)
            
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