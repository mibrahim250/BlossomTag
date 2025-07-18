# loading_screen.py – Sakura Loading Screens
# --------------------------------------------------------------------

import time
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar

class SakuraLoadingScreen(QDialog):
    def __init__(self, message="Loading...", parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF Sakura 🌸")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        
        # Sakura theme colors
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFE5E5, stop:1 #FFF0F5);
                border: 3px solid #FFB6C1;
                border-radius: 15px;
            }
            QLabel {
                color: #8B4B7A;
                background: transparent;
            }
            QProgressBar {
                border: 2px solid #FFB6C1;
                border-radius: 8px;
                background: #FFF0F5;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFB6C1, stop:1 #DDA0DD);
                border-radius: 6px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title with sakura emoji
        title = QLabel("🌸 PDF Sakura 🌸")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Loading message
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        msg_font = QFont()
        msg_font.setPointSize(11)
        self.message_label.setFont(msg_font)
        layout.addWidget(self.message_label)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        
        # Cute loading text
        self.cute_label = QLabel("Preparing your beautiful PDFs... 🌸")
        self.cute_label.setAlignment(Qt.AlignCenter)
        cute_font = QFont()
        cute_font.setPointSize(9)
        cute_font.setItalic(True)
        self.cute_label.setFont(cute_font)
        layout.addWidget(self.cute_label)
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        
        # Cute messages rotation
        self.cute_messages = [
            "Preparing your beautiful PDFs... 🌸",
            "Organizing sakura annotations... 🌺", 
            "Adding magical highlights... ✨",
            "Making everything pretty... 💕",
            "Almost ready for Riley... 🎀"
        ]
        self.message_index = 0

    def start_loading(self, duration_ms=3000):
        """Start the loading animation"""
        self.show()
        self.timer.start(50)  # Update every 50ms
        self.total_duration = duration_ms
        self.elapsed = 0
        
    def update_progress(self):
        self.elapsed += 50
        progress = min(100, (self.elapsed / self.total_duration) * 100)
        self.progress.setValue(int(progress))
        
        # Update cute message every 600ms
        if self.elapsed % 600 == 0:
            self.message_index = (self.message_index + 1) % len(self.cute_messages)
            self.cute_label.setText(self.cute_messages[self.message_index])
        
        if progress >= 100:
            self.timer.stop()
            QTimer.singleShot(500, self.accept)  # Close after brief pause

    def update_message(self, new_message):
        """Update the main message"""
        self.message_label.setText(new_message)

class ExportLoadingScreen(SakuraLoadingScreen):
    def __init__(self, parent=None):
        super().__init__("Exporting your annotated PDF...", parent)
        self.cute_messages = [
            "Creating beautiful exports... 🌸",
            "Preserving your highlights... 💕", 
            "Making annotations permanent... ✨",
            "Packaging with love... 🎀",
            "Almost done, Riley! 🌺"
        ]