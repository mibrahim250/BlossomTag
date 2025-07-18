# export_dialog.py – Export Options Dialog
# --------------------------------------------------------------------

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QDialog, QCheckBox, QRadioButton, QButtonGroup, QFrame
)

from ui_components import ACCENT

class ExportOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Options")
        self.setModal(True)
        self.resize(400, 250)
        self.setStyleSheet(f"""
            QDialog {{background:#2a2a2a;color:white;border:2px solid {ACCENT};border-radius:10px}}
            QRadioButton, QCheckBox {{color:white;padding:8px;}}
            QRadioButton::indicator, QCheckBox::indicator {{width:16px;height:16px;}}
            QPushButton {{background:{ACCENT};color:white;border:none;border-radius:8px;
                          padding:10px 20px;font-weight:bold}}
            QPushButton:hover {{background:#d8b9f1}}
            QFrame {{border:1px solid {ACCENT};border-radius:8px;padding:10px;margin:5px;}}
        """)
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("🖴 Export PDF Options")
        title.setStyleSheet("font-size:16px;font-weight:bold;")
        layout.addWidget(title)

        # Annotation style options
        style_frame = QFrame()
        style_layout = QVBoxLayout(style_frame)
        
        style_layout.addWidget(QLabel("📝 What to include:"))
        
        self.style_group = QButtonGroup()
        
        self.highlights_only = QRadioButton("Highlights Only")
        self.highlights_only.setToolTip("Just colored highlights, clean and simple")
        self.style_group.addButton(self.highlights_only, 0)
        style_layout.addWidget(self.highlights_only)
        
        self.full_annotations = QRadioButton("Highlights + Annotations")
        self.full_annotations.setToolTip("Highlights with tabs and tag information")
        self.style_group.addButton(self.full_annotations, 1)
        style_layout.addWidget(self.full_annotations)
        
        # Set default to full annotations
        self.full_annotations.setChecked(True)
        
        layout.addWidget(style_frame)

        # Quality option
        options_frame = QFrame()
        options_layout = QVBoxLayout(options_frame)
        
        options_layout.addWidget(QLabel("⚙️ Quality:"))
        
        self.high_quality = QCheckBox("High Quality Export")
        self.high_quality.setChecked(True)
        self.high_quality.setToolTip("Better quality but larger file size")
        options_layout.addWidget(self.high_quality)
        
        layout.addWidget(options_frame)

        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        export_btn = QPushButton("🖴 Export PDF")
        
        cancel_btn.clicked.connect(self.reject)
        export_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)

    def get_export_options(self):
        """Return the selected export options"""
        return {
            'include_annotations': self.full_annotations.isChecked(),
            'high_quality': self.high_quality.isChecked()
        }