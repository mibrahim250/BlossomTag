# dialogs.py – Dialog Windows and Forms (Fixed)
# --------------------------------------------------------------------

from pathlib import Path

from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QLineEdit, QTextEdit, QPushButton, 
    QDialog, QCheckBox, QMessageBox, QComboBox, QFrame
)

from ui_components import ACCENT, HIGHLIGHT_COLORS

# ───────────── Tag dialog ─────────────
class TagDialog(QDialog):
    def __init__(self, accent, data=None, parent=None, readonly=False):
        super().__init__(parent)
        self.setWindowTitle("Add Tag" if data is None else "View Tag")
        self.setModal(True); self.resize(450, 320)
        self.setStyleSheet(f"""
            QDialog {{background:#2a2a2a;color:white;border:2px solid {accent};border-radius:10px}}
            QLineEdit,QTextEdit {{background:#3a3a3a;border:2px solid {accent};
                                  border-radius:8px;color:white;padding:8px}}
            QPushButton {{background:{accent};color:white;border:none;border-radius:8px;
                          padding:10px 20px;font-weight:bold}}
            QPushButton:hover {{background:#d8b9f1}}
            QCheckBox {{color:white}}
        """)
        lay = QVBoxLayout(self); lay.setContentsMargins(20, 20, 20, 20); lay.setSpacing(12)

        lay.addWidget(QLabel("Tag Title:"))
        self.title_edit = QLineEdit(placeholderText="Enter title…")
        lay.addWidget(self.title_edit)

        lay.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit(placeholderText="Optional notes…", maximumHeight=110)
        lay.addWidget(self.desc_edit)

        self.printable_chk = QCheckBox("Make annotation printable")
        self.printable_chk.setChecked(True); lay.addWidget(self.printable_chk)

        row = QHBoxLayout(); lay.addLayout(row)
        cancel = QPushButton("Cancel"); save = QPushButton("Save Tag")
        row.addWidget(cancel); row.addWidget(save)
        cancel.clicked.connect(self.reject); save.clicked.connect(self.accept)
        save.setDefault(True); save.setAutoDefault(True)

        for w in (self.title_edit, self.desc_edit):
            w.installEventFilter(self)

        if data:
            self.title_edit.setText(data["title"])
            self.desc_edit.setText(data["desc"])
            self.printable_chk.setChecked(data.get("printable", True))

        if readonly:
            for w in (self.title_edit, self.desc_edit, self.printable_chk):
                w.setEnabled(False)
            save.hide(); cancel.setText("Close")

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.KeyPress and ev.key() in (Qt.Key_Return, Qt.Key_Enter):
            if not (ev.modifiers() & Qt.ShiftModifier):
                self.accept(); return True
        return super().eventFilter(obj, ev)

    def get_data(self):
        return {"title": self.title_edit.text().strip(),
                "desc":  self.desc_edit.toPlainText().strip(),
                "printable": self.printable_chk.isChecked()}

# ───────────── Preset Manager (CREATE/EDIT/DELETE ONLY) ─────────────
class PresetsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preset Manager")
        self.setModal(True); self.resize(600, 450)
        self.setStyleSheet(f"""
            QDialog {{background:#2a2a2a;color:white;border:2px solid {ACCENT};border-radius:10px}}
            QListWidget {{background:#1e1e1e;border:2px solid {ACCENT};border-radius:8px;padding:8px;}}
            QListWidget::item {{background:#3a3a3a;color:white;border-radius:6px;
                                margin:2px;padding:8px;}}
            QListWidget::item:selected {{background:{ACCENT};}}
            QListWidget::item:hover {{background:#4a4a4a;}}
            QLineEdit,QTextEdit {{background:#3a3a3a;border:2px solid {ACCENT};
                                  border-radius:8px;color:white;padding:8px}}
            QPushButton {{background:{ACCENT};color:white;border:none;border-radius:8px;
                          padding:8px 16px;font-weight:bold}}
            QPushButton:hover {{background:#d8b9f1}}
            QPushButton:disabled {{background:#555;color:#999;}}
            QComboBox {{background:#3a3a3a;border:2px solid {ACCENT};border-radius:8px;
                        color:white;padding:8px;}}
        """)
        
        self.presets = self.load_presets()
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("🎨 Preset Manager")
        header.setStyleSheet("font-size:16px;font-weight:bold;margin-bottom:10px;")
        main_layout.addWidget(header)
        
        info = QLabel("Create and manage your highlighting presets. Use them by highlighting text in the PDF.")
        info.setStyleSheet("color:#aaa;font-style:italic;margin-bottom:15px;")
        info.setWordWrap(True)
        main_layout.addWidget(info)
        
        # Main content with two columns
        content_layout = QHBoxLayout()
        
        # Left side - preset list
        left = QVBoxLayout()
        left.addWidget(QLabel("📌 Your Presets:"))
        self.preset_list = QListWidget()
        self.preset_list.itemClicked.connect(self.load_preset_details)
        left.addWidget(self.preset_list)
        
        # List action buttons
        list_btn_row = QHBoxLayout()
        self.edit_btn = QPushButton("✏️ Edit")
        self.delete_btn = QPushButton("🗑️ Delete")
        self.edit_btn.clicked.connect(self.edit_preset)
        self.delete_btn.clicked.connect(self.delete_preset)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        list_btn_row.addWidget(self.edit_btn)
        list_btn_row.addWidget(self.delete_btn)
        left.addLayout(list_btn_row)
        
        # Right side - create/edit form
        right = QVBoxLayout()
        right.addWidget(QLabel("🌸 Create New Preset:"))
        
        right.addWidget(QLabel("Preset Name:"))
        self.name_edit = QLineEdit(placeholderText="e.g., 'Stage Right', 'Important Notes'...")
        right.addWidget(self.name_edit)
        
        right.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit(placeholderText="Optional description...", maximumHeight=80)
        right.addWidget(self.desc_edit)
        
        right.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(HIGHLIGHT_COLORS.keys())
        right.addWidget(self.color_combo)
        
        self.printable_chk = QCheckBox("Make printable by default")
        self.printable_chk.setChecked(True)
        right.addWidget(self.printable_chk)
        
        # Form buttons
        form_btn_row = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save Preset")
        self.clear_btn = QPushButton("🔄 Clear Form")
        self.save_btn.clicked.connect(self.save_preset)
        self.clear_btn.clicked.connect(self.clear_form)
        form_btn_row.addWidget(self.clear_btn)
        form_btn_row.addWidget(self.save_btn)
        right.addLayout(form_btn_row)
        
        right.addStretch()
        
        # Add to content layout
        content_layout.addLayout(left, 1)
        content_layout.addLayout(right, 1)
        main_layout.addLayout(content_layout)
        
        # Bottom close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        main_layout.addWidget(close_btn)

    def load_presets(self):
        """Load presets from file"""
        import json
        try:
            presets_file = Path.home() / ".atnolol_presets.json"
            if presets_file.exists():
                with open(presets_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_presets_to_file(self):
        """Save presets to file"""
        import json
        try:
            presets_file = Path.home() / ".atnolol_presets.json"
            with open(presets_file, 'w') as f:
                json.dump(self.presets, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Couldn't save presets: {e}")

    def refresh_list(self):
        self.preset_list.clear()
        for name, preset in self.presets.items():
            color_name = preset.get('color', 'Purple')
            item = QListWidgetItem(f"🎨 {name} ({color_name})")
            item.setData(Qt.UserRole, name)
            self.preset_list.addItem(item)
        
        # Update button states
        has_selection = self.preset_list.currentItem() is not None
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def load_preset_details(self, item):
        """Load preset details into form for editing"""
        preset_name = item.data(Qt.UserRole)
        preset = self.presets.get(preset_name, {})
        
        self.name_edit.setText(preset_name)
        self.desc_edit.setText(preset.get('desc', ''))
        if preset.get('color') in HIGHLIGHT_COLORS:
            self.color_combo.setCurrentText(preset['color'])
        self.printable_chk.setChecked(preset.get('printable', True))
        
        # Update button states
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        
        # Change save button to update mode
        self.save_btn.setText("✏️ Update Preset")

    def save_preset(self):
        """Save or update preset"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Enter a preset name.")
            return
        
        preset = {
            'title': name,
            'desc': self.desc_edit.toPlainText().strip(),
            'color': self.color_combo.currentText(),
            'printable': self.printable_chk.isChecked()
        }
        
        self.presets[name] = preset
        self.save_presets_to_file()
        self.refresh_list()
        self.clear_form()
        
        QMessageBox.information(self, "Saved", f"Preset '{name}' saved successfully!")

    def edit_preset(self):
        """Edit selected preset (already loaded into form)"""
        # Form is already populated, just save
        self.save_preset()

    def delete_preset(self):
        """Delete selected preset"""
        current = self.preset_list.currentItem()
        if not current:
            return
        
        preset_name = current.data(Qt.UserRole)
        if QMessageBox.question(self, "Delete Preset", f"Delete '{preset_name}'?",
                               QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            del self.presets[preset_name]
            self.save_presets_to_file()
            self.refresh_list()
            self.clear_form()

    def clear_form(self):
        """Clear the form"""
        self.name_edit.clear()
        self.desc_edit.clear()
        self.color_combo.setCurrentText("Purple")
        self.printable_chk.setChecked(True)
        self.save_btn.setText("💾 Save Preset")
        self.preset_list.clearSelection()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

# ───────────── Enhanced Quick Preset Dialog (After Highlighting) - FIXED ─────────────
class QuickPresetDialog(QDialog):
    def __init__(self, selected_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🌸 Quick Tag")
        self.setModal(True)
        self.resize(400, 300)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setStyleSheet(f"""
            QDialog {{background:#2a2a2a;color:white;border:2px solid {ACCENT};border-radius:10px}}
            QComboBox {{background:#3a3a3a;border:2px solid {ACCENT};border-radius:8px;
                       color:white;padding:8px;font-size:12px;}}
            QComboBox::drop-down {{border:none;}}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin: 5px;
            }}
            QComboBox QAbstractItemView {{
                background:#3a3a3a;color:white;border:1px solid {ACCENT};
                selection-background-color:{ACCENT};
            }}
            QPushButton {{background:{ACCENT};color:white;border:none;border-radius:8px;
                          padding:8px 16px;font-weight:bold;font-size:12px;}}
            QPushButton:hover {{background:#d8b9f1}}
            QPushButton:pressed {{background:#b894d1}}
            QFrame {{border:1px solid {ACCENT};border-radius:8px;padding:8px;margin:4px;}}
            QLineEdit,QTextEdit {{background:#3a3a3a;border:2px solid {ACCENT};
                                  border-radius:8px;color:white;padding:8px;font-size:11px;}}
            QLabel {{color:white;font-size:11px;}}
        """)
        
        self.selected_text = selected_text[:80] + "..." if len(selected_text) > 80 else selected_text
        self.tag_data = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header with selected text
        if self.selected_text:
            text_frame = QFrame()
            text_layout = QVBoxLayout(text_frame)
            text_layout.setContentsMargins(8, 6, 8, 6)
            
            text_layout.addWidget(QLabel("📝 Selected:"))
            
            selected_label = QLabel(f'"{self.selected_text}"')
            selected_label.setWordWrap(True)
            selected_label.setStyleSheet("font-style:italic;color:#ddd;background:#3a3a3a;padding:6px;border-radius:6px;font-size:10px;")
            text_layout.addWidget(selected_label)
            layout.addWidget(text_frame)

        # Quick preset dropdown
        preset_frame = QFrame()
        preset_layout = QVBoxLayout(preset_frame)
        preset_layout.setContentsMargins(8, 6, 8, 6)
        
        preset_layout.addWidget(QLabel("🎀 Quick Select:"))
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("-- Select a preset --", None)
        
        # Load presets from file
        try:
            import json
            presets_file = Path.home() / ".atnolol_presets.json"
            if presets_file.exists():
                with open(presets_file, 'r') as f:
                    presets = json.load(f)
                
                # Add recent/favorite presets first
                preset_items = []
                for name, preset in presets.items():
                    color_name = preset.get('color', 'Purple')
                    preset_items.append((name, preset, color_name))
                
                # Sort by name for consistent ordering
                preset_items.sort(key=lambda x: x[0].lower())
                
                for name, preset, color_name in preset_items:
                    display_text = f"✨ {name} ({color_name})"
                    self.preset_combo.addItem(display_text, preset)
        except Exception as e:
            print(f"Error loading presets: {e}")
        
        # Add separator and "Add New Tag" option
        self.preset_combo.addItem("─────────────────", None)
        self.preset_combo.addItem("➕ Add New Tag...", "NEW_TAG")
        
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)
        preset_layout.addWidget(self.preset_combo)
        layout.addWidget(preset_frame)

        # New tag form (initially hidden)
        self.new_tag_frame = QFrame()
        self.new_tag_frame.setVisible(False)
        new_tag_layout = QVBoxLayout(self.new_tag_frame)
        new_tag_layout.setContentsMargins(8, 6, 8, 6)
        
        new_tag_layout.addWidget(QLabel("🌸 Create New Tag:"))
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Tag title...")
        new_tag_layout.addWidget(self.title_edit)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Optional description...")
        self.desc_edit.setMaximumHeight(50)
        new_tag_layout.addWidget(self.desc_edit)
        
        # Color selection for new tags
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(HIGHLIGHT_COLORS.keys())
        self.color_combo.setCurrentText("Purple")
        color_layout.addWidget(self.color_combo)
        new_tag_layout.addLayout(color_layout)
        
        layout.addWidget(self.new_tag_frame)

        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.apply_btn = QPushButton("🌸 Apply")
        self.apply_btn.setEnabled(False)  # Disabled until selection made
        
        self.cancel_btn.clicked.connect(self.reject)
        self.apply_btn.clicked.connect(self._apply_selection)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        layout.addLayout(button_layout)

        # Set focus to preset combo for quick keyboard navigation
        self.preset_combo.setFocus()

    def _on_preset_selected(self, index):
        """Handle preset selection from dropdown"""
        data = self.preset_combo.itemData(index)
        
        if data is None:
            # No selection or separator
            self.new_tag_frame.setVisible(False)
            self.apply_btn.setEnabled(False)
            self.apply_btn.setText("🌸 Apply")
        elif data == "NEW_TAG":
            # Show new tag form
            self.new_tag_frame.setVisible(True)
            self.apply_btn.setEnabled(True)
            self.apply_btn.setText("🌸 Create & Apply")
            self.title_edit.setFocus()
            # Adjust dialog size
            self.resize(400, 400)
        else:
            # Preset selected
            self.new_tag_frame.setVisible(False)
            self.apply_btn.setEnabled(True)
            self.apply_btn.setText(f"🌸 Apply '{self.preset_combo.currentText().split(' (')[0].replace('✨ ', '')}'")
            # Shrink dialog back
            self.resize(400, 300)

    def _apply_selection(self):
        """Apply the selected preset or create new tag"""
        selected_data = self.preset_combo.itemData(self.preset_combo.currentIndex())
        
        if selected_data == "NEW_TAG":
            # Create new tag
            title = self.title_edit.text().strip()
            if not title:
                QMessageBox.warning(self, "Missing Title", "Please enter a tag title.")
                return
            
            self.tag_data = {
                "title": title,
                "desc": self.desc_edit.toPlainText().strip(),
                "color": self.color_combo.currentText(),  # Store color name, not QColor object
                "printable": True
            }
        elif selected_data:
            # Use existing preset - make sure we copy it properly
            self.tag_data = selected_data.copy()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a preset or create a new tag.")
            return
        
        self.accept()

    def get_tag_data(self):
        """Return the selected/created tag data"""
        return self.tag_data

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.apply_btn.isEnabled():
                self._apply_selection()
        else:
            super().keyPressEvent(event)