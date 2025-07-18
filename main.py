# main.py – Main Window and Application Entry Point (Production Safe)
# --------------------------------------------------------------------

import sys
import os
import traceback
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QAction, QIcon
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QTabWidget, QToolBar, 
        QFileDialog, QComboBox, QLabel, QLineEdit, QMessageBox
    )
except ImportError as e:
    print(f"Error importing PySide6: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)

try:
    from ui_components import (
        ACCENT, HIGHLIGHT_COLORS, CloseableTabBar, setup_app_palette
    )
    from pdf_annotator import PDFPane
except ImportError as e:
    print(f"Error importing application modules: {e}")
    traceback.print_exc()
    sys.exit(1)

# Global exception handler
def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions gracefully"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"Uncaught exception: {error_msg}")
    
    # Show user-friendly error dialog
    try:
        app = QApplication.instance()
        if app:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("BlossomTag Error")
            msg.setText("An unexpected error occurred.")
            msg.setDetailedText(error_msg)
            msg.setInformativeText("The application will continue running. You can save your work and restart if needed.")
            msg.exec()
    except:
        pass

# Install global exception handler
sys.excepthook = handle_exception

# ────────────────────── Main window ──────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.setWindowTitle("BlossomTag - Beautiful PDF Annotation Tool")
            self.resize(1500, 900)
            
            # Set application icon if available
            icon_path = Path("icon.ico")
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
            
            setup_app_palette()
            
            self.tabs = QTabWidget()
            self.tabs.setTabBar(CloseableTabBar())
            self.tabs.tabCloseRequested.connect(self._close_tab)
            self.tabs.currentChanged.connect(self._tab_changed)
            self.setCentralWidget(self.tabs)
            self._setup_toolbar()
            
            # Auto-save timer
            self.autosave_timer = QTimer()
            self.autosave_timer.timeout.connect(self._autosave_all)
            self.autosave_timer.start(30000)  # Auto-save every 30 seconds
            
        except Exception as e:
            self._show_error("Initialization Error", f"Failed to initialize main window: {e}")

    def _show_error(self, title, message):
        """Show error message to user"""
        try:
            QMessageBox.critical(self, title, message)
        except:
            print(f"Error: {title} - {message}")

    def _autosave_all(self):
        """Auto-save all open documents"""
        try:
            for i in range(self.tabs.count()):
                pane = self.tabs.widget(i)
                if pane and hasattr(pane, 'viewer'):
                    pane.viewer._auto_save()
        except Exception as e:
            print(f"Auto-save error: {e}")

    def _toggle_text_detection(self, checked):
        """Toggle text detection overlay"""
        try:
            if self._current_pane():
                self._current_pane().viewer.toggle_text_detection(checked)
        except Exception as e:
            self._show_error("Text Detection Error", str(e))

    def _tab_changed(self):
        """Update page display when tab changes"""
        self._update_page_display()

    def _setup_toolbar(self):
        try:
            tb = QToolBar()
            self.addToolBar(tb)
            tb.setStyleSheet(f"""
                QToolBar {{background:#2a2a2a;padding:4px;spacing:6px;
                            border-bottom:2px solid {ACCENT};}}
                QToolButton {{background:#3a3a3a;color:white;border:1px solid #555;
                               border-radius:6px;padding:4px 8px;}}
                QToolButton:hover {{background:#505050;}}
            """)
            
            # File operations
            tb.addAction(QAction("📂 Open PDF", self, triggered=self._open))
            tb.addAction(QAction("📋 Load Annotations", self,
                                 triggered=lambda: self._safe_call(lambda: self._current_pane().load_annotations())))
            tb.addSeparator()
            
            # Save/Export operations  
            tb.addAction(QAction("💾 Save Annotations", self,
                                 triggered=lambda: self._safe_call(lambda: self._current_pane().save_annotations())))
            tb.addAction(QAction("🖴 Export Final PDF", self,
                                 triggered=lambda: self._safe_call(lambda: self._current_pane().export())))
            tb.addSeparator()
            
            # Navigation with page number
            tb.addAction(QAction("◀", self,
                                 triggered=lambda: self._safe_call(lambda: 
                                 self._current_pane().viewer.goto(self._current_pane().viewer.page - 1))))
            
            # Page number input
            tb.addWidget(QLabel("Page:"))
            self.page_input = QLineEdit()
            self.page_input.setMaximumWidth(50)
            self.page_input.setPlaceholderText("1")
            self.page_input.returnPressed.connect(self._goto_page)
            tb.addWidget(self.page_input)
            
            self.page_label = QLabel("/ ?")
            tb.addWidget(self.page_label)
            
            tb.addAction(QAction("▶", self,
                                 triggered=lambda: self._safe_call(lambda:
                                 self._current_pane().viewer.goto(self._current_pane().viewer.page + 1))))
            tb.addSeparator()
            
            # Zoom controls
            tb.addAction(QAction("🔍+ Zoom In", self,
                                 triggered=lambda: self._safe_call(lambda: self._current_pane().zoom_in())))
            tb.addAction(QAction("🔍- Zoom Out", self,
                                 triggered=lambda: self._safe_call(lambda: self._current_pane().zoom_out())))
            tb.addAction(QAction("📏 Fit Width", self,
                                 triggered=lambda: self._safe_call(lambda: self._current_pane().fit_to_width())))
            tb.addAction(QAction("🔄 Reset Zoom", self,
                                 triggered=lambda: self._safe_call(lambda: self._current_pane().reset_zoom())))
            tb.addSeparator()
            
            # Sidebar toggle
            tb.addAction(QAction("📑 Tags", self,
                                 triggered=lambda: self._safe_call(lambda: self._current_pane().toggle_sidebar())))
            tb.addAction(QAction("🎨 Preset Manager", self,
                                 triggered=lambda: self._safe_call(lambda: self._current_pane().open_presets())))
            
            # Text detection toggle
            self.text_detection_action = QAction("👁️ Show Text", self, checkable=True)
            self.text_detection_action.triggered.connect(self._toggle_text_detection)
            tb.addAction(self.text_detection_action)
            
            tb.addSeparator()

            # Color picker
            tb.addWidget(QLabel("Color:"))
            color_combo = QComboBox()
            color_combo.addItems(HIGHLIGHT_COLORS.keys())
            color_combo.setCurrentText("Purple")
            color_combo.currentTextChanged.connect(
                lambda name: self._safe_call(lambda:
                self._current_pane().viewer.set_highlight_color(HIGHLIGHT_COLORS[name])))
            tb.addWidget(color_combo)
            
        except Exception as e:
            self._show_error("Toolbar Setup Error", str(e))

    def _safe_call(self, func):
        """Safely call a function with error handling"""
        try:
            if self._current_pane():
                return func()
        except Exception as e:
            self._show_error("Operation Error", str(e))

    def _goto_page(self):
        """Go to page number entered in page input"""
        try:
            page_num = int(self.page_input.text()) - 1  # Convert to 0-based
            if self._current_pane():
                self._current_pane().viewer.goto(page_num)
        except ValueError:
            pass  # Ignore invalid input
        except Exception as e:
            self._show_error("Navigation Error", str(e))

    def _update_page_display(self):
        """Update page number display"""
        try:
            pane = self._current_pane()
            if pane and pane.viewer.doc:
                current = pane.viewer.page + 1  # Convert to 1-based
                total = len(pane.viewer.doc)
                self.page_input.setPlaceholderText(str(current))
                self.page_label.setText(f"/ {total}")
            else:
                self.page_input.setPlaceholderText("1")
                self.page_label.setText("/ ?")
        except Exception as e:
            print(f"Page display update error: {e}")

    def _current_pane(self):
        """Get the currently active PDF pane"""
        try:
            return self.tabs.currentWidget()
        except:
            return None

    def _open(self):
        """Open PDF file(s) and create new tabs"""
        try:
            paths, _ = QFileDialog.getOpenFileNames(
                self, "Open PDF(s)", str(Path.home()), "PDF Files (*.pdf)")
            
            for path in paths:
                try:
                    pane = PDFPane()
                    if pane.load(path):
                        self.tabs.addTab(pane, Path(path).name)
                        self.tabs.setCurrentWidget(pane)
                        # Connect page change signal
                        if hasattr(pane.viewer, 'page_changed'):
                            pane.viewer.page_changed.connect(self._update_page_display)
                        self._update_page_display()
                    else:
                        pane.deleteLater()
                except Exception as e:
                    self._show_error("File Open Error", f"Failed to open {Path(path).name}: {e}")
                    
        except Exception as e:
            self._show_error("Open Dialog Error", str(e))

    def _close_tab(self, index):
        """Close a tab and clean up the widget"""
        try:
            widget = self.tabs.widget(index)
            if widget:
                # Auto-save before closing
                if hasattr(widget, 'viewer') and hasattr(widget.viewer, '_auto_save'):
                    widget.viewer._auto_save()
                widget.deleteLater()
            self.tabs.removeTab(index)
        except Exception as e:
            print(f"Tab close error: {e}")

    def closeEvent(self, event):
        """Handle application close"""
        try:
            # Auto-save all before closing
            self._autosave_all()
            event.accept()
        except Exception as e:
            print(f"Close error: {e}")
            event.accept()

# ─────────────────────────── Entry Point ───────────────────────────
def main():
    """Main application entry point with comprehensive error handling"""
    try:
        # Create application
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("BlossomTag")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("BlossomTag")
        app.setApplicationDisplayName("BlossomTag - Beautiful PDF Annotation Tool")
        
        # Handle high DPI displays
        try:
            app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        except:
            pass  # Ignore if not available
        
        # Create and show main window
        try:
            window = MainWindow()
            window.show()
        except Exception as e:
            QMessageBox.critical(None, "Startup Error", 
                               f"Failed to create main window: {e}\n\nThe application will exit.")
            return 1
        
        # Start the application event loop
        return app.exec()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Please ensure all required packages are installed:")
        print("pip install PySide6 PyMuPDF Pillow pytesseract")
        return 1
    except Exception as e:
        print(f"Fatal Error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)