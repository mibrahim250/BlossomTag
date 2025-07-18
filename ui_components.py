# ui_components.py – UI Widgets and Dialogs
# --------------------------------------------------------------------

import textwrap
from pathlib import Path
from PySide6.QtCore import (
    Qt, QPoint, QTimer, QEvent,
    QPropertyAnimation, QEasingCurve
)
from PySide6.QtGui import (
    QColor, QPalette, QAction, QFont
)
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QTabBar,
    QLabel, QLineEdit, QTextEdit, QPushButton, 
    QDialog, QCheckBox, QFrame, QMessageBox, QComboBox
)

# ─────────────────────────── THEME ───────────────────────────
ACCENT = "#C7B0E2"
HIGHLIGHT_COLORS = {
    "Hot Pink": QColor(255, 20, 147, 120),
    "Lavender": QColor(230, 230, 250, 120),
    "Purple":   QColor(199, 176, 226, 120),
    "Plum":     QColor(221, 160, 221, 120),
    "Orchid":   QColor(218, 112, 214, 120),
    "Violet":   QColor(238, 130, 238, 120),
    "Yellow":   QColor(255, 255,   0, 120),
    "Red":      QColor(255,   0,   0, 120),
    "Green":    QColor(  0, 255,   0, 120),
    "Blue":     QColor( 30, 144, 255, 120),
    "Teal":     QColor(  0, 200, 200, 120),
    "Orange":   QColor(255, 165,   0, 120),
    "Mint":     QColor(152, 255, 152, 120),
    "Slate":    QColor(112, 128, 144, 120),
    "ibhe fav": QColor(249, 203,  41, 120),  # 💛
    "Coral":    QColor(255, 127,  80, 120),  # 🧡 NEW
    "Lime":     QColor(50,  205,  50, 120),  # 💚 NEW
    "Sky":      QColor(135, 206, 235, 120),  # 💙 NEW
    "Rose":     QColor(255, 105, 180, 120),  # 🌹 NEW
    "Gold":     QColor(255, 215,   0, 120),  # ✨ NEW
}

# ───────────────────── Message-style pop-ups ─────────────────────
class SleekTagPopup(QFrame):
    """Bubble shown when clicking tabs in the margin."""
    def __init__(self, tag, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(f"""
            QFrame {{background:white;border-radius:12px;border:2px solid {ACCENT};}}
            QLabel {{color:#222;background:transparent;}}
            QPushButton {{background:#ff4444;color:white;border:none;border-radius:10px;
                          font-weight:bold;padding:4px;}}
            QPushButton:hover {{background:#ff6666;}}
        """)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Create header layout
        header_layout = QHBoxLayout()
        
        # Title
        ttl = tag.get("title", "Untitled").strip()
        t_lbl = QLabel(ttl)
        f = QFont()
        f.setBold(True)
        t_lbl.setFont(f)
        header_layout.addWidget(t_lbl)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        # Add header to main layout
        main_layout.addLayout(header_layout)

        # Description
        desc = tag.get("desc", "").strip()
        if desc:
            d_lbl = QLabel(desc)
            d_lbl.setWordWrap(True)
            main_layout.addWidget(d_lbl)

        self.adjustSize()
        self._fade = QPropertyAnimation(self, b"windowOpacity",
                                        duration=200,
                                        startValue=0.0, endValue=1.0,
                                        easingCurve=QEasingCurve.OutCubic)

    def show_at(self, gp):
        self.move(gp); self.show(); self._fade.start()
        # Don't auto-close anymore, user controls it

    def mousePressEvent(self, _): 
        # Only close if clicking outside content area, not the close button
        pass


class ToastPopup(QFrame):
    """Bottom-right toast for quick status ("Tag saved!")."""
    def __init__(self, msg, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(f"""
            QFrame {{background:#323232;border-radius:10px;}}
            QLabel {{color:white;padding:8px 14px;}}
        """)
        lay = QHBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(QLabel(f"✅  {msg}"))
        self.adjustSize()

        # Fade-in / slide-up anim
        self._anim_op = QPropertyAnimation(self, b"windowOpacity",
                                           duration=300,
                                           startValue=0.0, endValue=1.0,
                                           easingCurve=QEasingCurve.OutCubic)
        self._anim_pos = QPropertyAnimation(self, b"pos",
                                            duration=300,
                                            easingCurve=QEasingCurve.OutCubic)

    def show_in(self, parent_rect):
        margin = 20
        tgt = QPoint(parent_rect.right() - self.width() - margin,
                     parent_rect.bottom() - self.height() - margin)
        self.move(tgt + QPoint(0, 30))     # start slightly lower
        self.show()
        self._anim_pos.setStartValue(self.pos())
        self._anim_pos.setEndValue(tgt)
        self._anim_op.start(); self._anim_pos.start()
        QTimer.singleShot(800, self._fade_out)  # Changed from 1000 to 800ms

    def _fade_out(self):
        fade = QPropertyAnimation(self, b"windowOpacity",
                                  duration=200,  # Faster fade out
                                  startValue=1.0, endValue=0.0,
                                  easingCurve=QEasingCurve.InCubic)
        fade.finished.connect(self.deleteLater)
        fade.start()

# ───────────── Closeable draggable tab-bar ─────────────
class CloseableTabBar(QTabBar):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True); self.setMovable(True)
        self.setStyleSheet(f"""
            QTabBar::tab {{background:#3a3a3a;color:white;padding:8px 16px;margin-right:2px;
                           border-top-left-radius:8px;border-top-right-radius:8px;}}
            QTabBar::tab:selected {{background:{ACCENT};}}
            QTabBar::tab:hover {{background:#4a4a4a;}}
            QTabBar::close-button {{image:none;background:rgba(255,255,255,0.3);
                                    border-radius:6px;margin:2px;}}
            QTabBar::close-button:hover {{background:rgba(255,0,0,0.7);}}
        """)

# ───────────── Enhanced Tag dialog with presets ─────────────
class TagDialog(QDialog):
    def __init__(self, accent, data=None, parent=None, readonly=False):
        super().__init__(parent)
        self.setWindowTitle("Add Tag" if data is None else "View Tag")
        self.setModal(True)
        self.resize(650, 400)  # Made wider for presets
        self.setStyleSheet(f"""
            QDialog {{background:#2a2a2a;color:white;border:2px solid {accent};border-radius:10px}}
            QLineEdit,QTextEdit {{background:#3a3a3a;border:2px solid {accent};
                                  border-radius:8px;color:white;padding:8px}}
            QPushButton {{background:{accent};color:white;border:none;border-radius:8px;
                          padding:10px 20px;font-weight:bold}}
            QPushButton:hover {{background:#d8b9f1}}
            QCheckBox {{color:white}}
            QListWidget {{background:#1e1e1e;border:2px solid {accent};border-radius:8px;padding:4px;}}
            QListWidget::item {{background:#3a3a3a;color:white;border-radius:4px;
                                margin:2px;padding:6px;}}
            QListWidget::item:selected {{background:{accent};}}
            QListWidget::item:hover {{background:#4a4a4a;}}
            QComboBox {{background:#3a3a3a;border:2px solid {accent};border-radius:8px;
                       color:white;padding:8px;}}
        """)
        
        # Main layout - horizontal split
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Left side - Presets
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("🎨 Quick Presets:"))
        
        self.presets_list = QListWidget()
        self.presets_list.setMaximumWidth(200)
        self.presets_list.setMaximumHeight(250)
        self.presets_list.itemClicked.connect(self._load_preset)
        self.presets_list.itemDoubleClicked.connect(self._instant_preset)  # Double-click for instant tag
        left_layout.addWidget(self.presets_list)
        
        left_layout.addStretch()
        main_layout.addLayout(left_layout)

        # Right side - Form
        right_layout = QVBoxLayout()
        
        right_layout.addWidget(QLabel("Tag Title:"))
        self.title_edit = QLineEdit(placeholderText="Enter title…")
        right_layout.addWidget(self.title_edit)

        right_layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit(placeholderText="Optional notes…", maximumHeight=100)
        right_layout.addWidget(self.desc_edit)

        # Color selection
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(HIGHLIGHT_COLORS.keys())
        self.color_combo.setCurrentText("Purple")
        color_layout.addWidget(self.color_combo)
        right_layout.addLayout(color_layout)

        self.printable_chk = QCheckBox("Make annotation printable")
        self.printable_chk.setChecked(True)
        right_layout.addWidget(self.printable_chk)

        # Buttons
        button_layout = QHBoxLayout()
        cancel = QPushButton("Cancel")
        save = QPushButton("Save Tag")
        button_layout.addWidget(cancel)
        button_layout.addWidget(save)
        right_layout.addLayout(button_layout)
        
        main_layout.addLayout(right_layout)

        # Connect signals
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)
        save.setDefault(True)
        save.setAutoDefault(True)

        # Install event filters
        for w in (self.title_edit, self.desc_edit):
            w.installEventFilter(self)

        # Load presets
        self._load_presets()

        # Handle existing data
        if data:
            self.title_edit.setText(data["title"])
            self.desc_edit.setText(data["desc"])
            self.printable_chk.setChecked(data.get("printable", True))

        if readonly:
            for w in (self.title_edit, self.desc_edit, self.printable_chk, self.color_combo):
                w.setEnabled(False)
            save.hide()
            cancel.setText("Close")

    def _load_presets(self):
        """Load presets from file and populate list"""
        import json
        try:
            presets_file = Path.home() / ".atnolol_presets.json"
            if presets_file.exists():
                with open(presets_file, 'r') as f:
                    presets = json.load(f)
                
                for name, preset in presets.items():
                    color_name = preset.get('color', 'Purple')
                    item = QListWidgetItem(f"✨ {name}\n({color_name})")
                    item.setData(Qt.UserRole, preset)
                    self.presets_list.addItem(item)
        except Exception:
            pass

    def _load_preset(self, item):
        """Load a preset into the form"""
        preset = item.data(Qt.UserRole)
        if preset:
            self.title_edit.setText(preset.get('title', ''))
            self.desc_edit.setText(preset.get('desc', ''))
            if preset.get('color') in HIGHLIGHT_COLORS:
                self.color_combo.setCurrentText(preset['color'])
            self.printable_chk.setChecked(preset.get('printable', True))

    def _instant_preset(self, item):
        """Double-click preset = instant accept with that preset"""
        self._load_preset(item)
        self.accept()  # Instantly accept the dialog

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.KeyPress and ev.key() in (Qt.Key_Return, Qt.Key_Enter):
            if not (ev.modifiers() & Qt.ShiftModifier):
                self.accept()
                return True
        return super().eventFilter(obj, ev)

    def get_data(self):
        return {
            "title": self.title_edit.text().strip(),
            "desc": self.desc_edit.toPlainText().strip(),
            "color": self.color_combo.currentText(),
            "printable": self.printable_chk.isChecked()
        }

# ───────────────────── Tag Search Widget ─────────────────────
class TagSearchWidget(QFrame):
    """Search tags by title at the top of the sidebar"""
    
    def __init__(self, viewer, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.highlights = []
        
        self.setStyleSheet(f"""
            QFrame {{background:#1a1a1a;border:2px solid {ACCENT};border-radius:8px;
                     padding:8px;margin:4px;}}
            QLineEdit {{background:#3a3a3a;border:2px solid {ACCENT};border-radius:6px;
                       color:white;padding:6px;}}
            QListWidget {{background:#2a2a2a;border:1px solid {ACCENT};border-radius:6px;
                          max-height:150px;}}
            QListWidget::item {{background:#3a3a3a;color:white;border-radius:4px;
                                margin:1px;padding:6px;}}
            QListWidget::item:selected {{background:{ACCENT};}}
            QListWidget::item:hover {{background:#4a4a4a;}}
            QLabel {{color:white;}}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        
        # Header
        layout.addWidget(QLabel("🔍 Search Tags:"))
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search tags...")
        self.search_input.textChanged.connect(self._search_tags)
        layout.addWidget(self.search_input)
        
        # Results list (initially hidden)
        self.results_list = QListWidget()
        self.results_list.setVisible(False)
        self.results_list.itemDoubleClicked.connect(self._jump_to_tag)
        layout.addWidget(self.results_list)
        
        # Connect to viewer's highlight creation
        self.viewer.highlight_created.connect(self._add_highlight)
    
    def _add_highlight(self, highlight):
        """Add a highlight to our search index"""
        self.highlights.append(highlight)
    
    def _search_tags(self, text):
        """Search tags by title"""
        text = text.strip().lower()
        
        if not text:
            self.results_list.setVisible(False)
            return
        
        # Find matching highlights
        matches = []
        for hl in self.highlights:
            title = hl["tag"].get("title", "").lower()
            desc = hl["tag"].get("desc", "").lower()
            
            if text in title or text in desc:
                matches.append(hl)
        
        # Update results list
        self.results_list.clear()
        
        if matches:
            self.results_list.setVisible(True)
            for hl in matches:
                title = hl["tag"].get("title", "Untitled")
                page = hl["page"] + 1
                preview = hl["text"][:30] + "..." if len(hl["text"]) > 30 else hl["text"]
                
                item_text = f"📝 {title}\nPage {page}: {preview}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, hl)
                self.results_list.addItem(item)
        else:
            self.results_list.setVisible(False)
    
    def _jump_to_tag(self, item):
        """Jump to the selected tag's page"""
        highlight = item.data(Qt.UserRole)
        if highlight:
            self.viewer.jump_to_page(highlight["page"])
            # Clear search after jumping
            self.search_input.clear()
            self.results_list.setVisible(False)

# ───────────────────── Enhanced Sidebar with Search ─────────────────────
class TagSidebar(QFrame):
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.highlights = []
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        
        # Add search widget at the top
        self.search_widget = TagSearchWidget(viewer, self)
        layout.addWidget(self.search_widget)
        
        # Add the regular tags list
        self.tags_list = QListWidget()
        self.tags_list.setStyleSheet(f"""
            QListWidget {{background:#1e1e1e;border:2px solid {ACCENT};
                          border-radius:8px;padding:8px;}}
            QListWidget::item {{background:#2d4a3a;color:white;font-weight:bold;
                                border-radius:8px;margin:4px 2px;padding:12px;
                                border:1px solid #3a5a4a;}}
            QListWidget::item:selected {{background:#4CAF50;border:2px solid #66DD75;}}
            QListWidget::item:hover {{background:#3a5a4a;border:1px solid #4CAF50;}}
        """)
        
        layout.addWidget(QLabel("📑 All Tags:"))
        layout.addWidget(self.tags_list)
        
        # Connect signals
        self.viewer.highlight_created.connect(self._add)
        self.tags_list.itemDoubleClicked.connect(self._jump)
        self.tags_list.setContextMenuPolicy(Qt.ActionsContextMenu)
        self._ctx()

    def _ctx(self):
        self.tags_list.addAction(QAction("View Details", self,
                               triggered=lambda: self._dlg(True)))
        self.tags_list.addAction(QAction("Edit Tag", self,
                               triggered=lambda: self._dlg(False)))
        self.tags_list.addAction(QAction("Delete Tag", self, triggered=self._del))

    def _add(self, hl): 
        self.highlights.append(hl)
        self._ref(hl)

    def _ref(self, hl):
        ttl = hl["tag"]["title"] or "Untitled"
        prn = " 🖨️" if hl["tag"].get("printable", True) else ""
        txt = f"{ttl}{prn}\nPage {hl['page'] + 1}"
        it = next((i for i in self._find_items("", Qt.MatchContains)
                   if i.data(Qt.UserRole) == hl["id"]), None)
        if not it:
            it = QListWidgetItem()
            self.tags_list.addItem(it)
            it.setData(Qt.UserRole, hl["id"])
        it.setText(txt)
        tip = f"Title: {ttl}\nPage: {hl['page'] + 1}"
        if hl["tag"]["desc"]: tip += f"\n\n{hl['tag']['desc']}"
        it.setToolTip(tip)

    def _find_items(self, text, flag):
        """Helper to find items in the tags list"""
        items = []
        for i in range(self.tags_list.count()):
            item = self.tags_list.item(i)
            if item:
                items.append(item)
        return items

    def _cur(self):
        it = self.tags_list.currentItem()
        if not it: return None
        return next((h for h in self.highlights
                     if h["id"] == it.data(Qt.UserRole)), None)

    def _jump(self, _): 
        hl = self._cur()
        if hl: 
            self.viewer.jump_to_page(hl["page"])
            
    def _dlg(self, ro): 
        hl = self._cur()
        if hl: 
            dlg = TagDialog(ACCENT, hl["tag"], self, ro)
            dlg.exec()
            
    def _del(self):
        hl = self._cur()
        if hl and QMessageBox.question(self, "Delete?", "Remove this tag?",
                                       QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.viewer.remove_highlight(hl["id"])
            self.highlights.remove(hl)
            self.tags_list.takeItem(self.tags_list.currentRow())

def setup_app_palette():
    """Set up the dark theme palette for the application"""
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(42, 42, 42))
    pal.setColor(QPalette.Base, QColor(26, 26, 26))
    pal.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    pal.setColor(QPalette.Text, Qt.white)
    pal.setColor(QPalette.Button, QColor(ACCENT))
    pal.setColor(QPalette.ButtonText, Qt.white)
    pal.setColor(QPalette.Highlight, QColor(ACCENT))
    pal.setColor(QPalette.HighlightedText, Qt.white)
    QApplication.instance().setPalette(pal)