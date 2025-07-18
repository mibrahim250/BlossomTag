# pdf_annotator.py – PDF Annotation and Tagging System
# --------------------------------------------------------------------

import sys, io, textwrap
from pathlib import Path
import fitz       # PyMuPDF
from fitz import Quad

try:
    import pytesseract
    from PIL import Image
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\super\Desktop\onedriveshit\Desktop\Projects\atnoLOL\src\tessdata\Tesseract-OCR\tesseract.exe"
    OCR_ON = True
except ImportError:
    OCR_ON = False

from PySide6.QtCore import Qt, QRect, QPoint, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QPixmap, QImage, QCursor, QPolygon, QPen, QFont
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QScrollArea, QLabel, QFileDialog, QMessageBox, QDialog
)

from pdf_core import PdfCore
from ui_components import (
    ACCENT, HIGHLIGHT_COLORS, SleekTagPopup, ToastPopup, 
    TagDialog, TagSidebar
)

# ───────────────────────── PDF Annotator ─────────────────────────
class PdfAnnotator(PdfCore):
    """PDF viewer with annotation and tagging capabilities"""
    
    highlight_created = Signal(dict)
    TAB_W, TAB_H = 20, 50

    def __init__(self):
        super().__init__()
        
        # Annotation-specific properties
        self.highlights = []
        self.current_color = HIGHLIGHT_COLORS["Purple"]
        self.selecting = False
        self.start_point = self.end_point = None
        self.tab_rects = []
        self.popup = None
        self.current_preset = None

    # -------- file ops override --------
    def load(self, p: str):
        if super().load(p):
            self.highlights.clear()
            self._auto_load()
            return True
        return False

    def _auto_save(self):
        """Automatically save annotations alongside PDF"""
        if hasattr(self, 'original_path'):
            auto_file = str(Path(self.original_path).with_suffix('.atnolol'))
            self.save_annotations(auto_file)

    def _auto_load(self):
        """Automatically load annotations if they exist"""
        if hasattr(self, 'original_path'):
            auto_file = str(Path(self.original_path).with_suffix('.atnolol'))
            if Path(auto_file).exists():
                self.load_annotations(auto_file)

    # -------- annotation file operations --------
    def save_annotations(self, filepath=None):
        """Save current annotations to a JSON file"""
        if not filepath:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Save Annotations", 
                str(Path(self.original_path).with_suffix('.atnolol')),
                "atnoLOL Files (*.atnolol);;JSON Files (*.json)")
        if not filepath: 
            return False
        
        import json
        data = {
            "original_pdf": self.original_path,
            "highlights": []
        }
        
        for hl in self.highlights:
            hl_data = {
                "page": hl["page"],
                "pdf_rect": [hl["pdf_rect"].x0, hl["pdf_rect"].y0, 
                           hl["pdf_rect"].x1, hl["pdf_rect"].y1],
                "color": hl["color"].getRgb(),
                "text": hl["text"],
                "tag": hl["tag"],
                "id": hl["id"]
            }
            data["highlights"].append(hl_data)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save: {e}")
            return False

    def load_annotations(self, filepath=None):
        """Load annotations from a JSON file"""
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Load Annotations", str(Path.home()),
                "atnoLOL Files (*.atnolol);;JSON Files (*.json)")
        if not filepath: 
            return False
        
        import json
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load the original PDF if different
            if data["original_pdf"] != getattr(self, 'original_path', ''):
                if not super().load(data["original_pdf"]):
                    QMessageBox.warning(self, "PDF not found", 
                                      f"Original PDF not found: {data['original_pdf']}")
                    return False
            
            # Clear existing highlights
            self.highlights.clear()
            
            # Load highlights
            for hl_data in data["highlights"]:
                rect = fitz.Rect(hl_data["pdf_rect"])
                color = QColor(*hl_data["color"])
                
                hl = dict(
                    page=hl_data["page"],
                    pdf_rect=rect,
                    color=color,
                    text=hl_data["text"],
                    tag=hl_data["tag"],
                    id=hl_data["id"]
                )
                self.highlights.append(hl)
                self.highlight_created.emit(hl)
            
            self.update()
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load: {e}")
            return False

    # -------- text selection helpers --------
    def _snap_to_text(self, selection_rect):
        """Better text recognition - snap to actual text like normal text selection"""
        if not self.text_blocks:
            return "", None
            
        # Find all text blocks that intersect with selection
        intersecting_blocks = []
        selection_pdf = selection_rect
        
        for block in self.text_blocks:
            # Check if selection overlaps with text block
            if (selection_pdf.x0 <= block["rect"].x1 and selection_pdf.x1 >= block["rect"].x0 and
                selection_pdf.y0 <= block["rect"].y1 and selection_pdf.y1 >= block["rect"].y0):
                intersecting_blocks.append(block)
        
        if not intersecting_blocks:
            return "", None
            
        # Sort blocks by reading order (top to bottom, left to right)
        intersecting_blocks.sort(key=lambda b: (b["rect"].y0, b["rect"].x0))
        
        # Combine text from all intersecting blocks
        combined_text = " ".join(block["text"].strip() for block in intersecting_blocks)
        
        # Calculate bounding rect that covers all selected text
        if intersecting_blocks:
            min_x0 = min(block["rect"].x0 for block in intersecting_blocks)
            min_y0 = min(block["rect"].y0 for block in intersecting_blocks)
            max_x1 = max(block["rect"].x1 for block in intersecting_blocks)
            max_y1 = max(block["rect"].y1 for block in intersecting_blocks)
            
            snapped_rect = fitz.Rect(min_x0, min_y0, max_x1, max_y1)
            return combined_text.strip(), snapped_rect
        
        return "", None

    # -------- drawing helpers --------
    def _draw_tab(self, p, rect, col):
        """Draw a more visible tab with better styling"""
        # Make tab bigger and more visible
        tab_rect = QRect(rect.x() - 3, rect.y(), rect.width() + 6, rect.height())
        
        # Draw shadow first
        shadow_rect = tab_rect.adjusted(3, 3, 3, 3)
        pts_shadow = [QPoint(shadow_rect.left(), shadow_rect.top()),
                     QPoint(shadow_rect.right() - 10, shadow_rect.top()),
                     QPoint(shadow_rect.right(), shadow_rect.center().y()),
                     QPoint(shadow_rect.right() - 10, shadow_rect.bottom()),
                     QPoint(shadow_rect.left(), shadow_rect.bottom())]
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 100))
        p.drawPolygon(QPolygon(pts_shadow))
        
        # Draw main tab with border
        pts = [QPoint(tab_rect.left(), tab_rect.top()),
               QPoint(tab_rect.right() - 10, tab_rect.top()),
               QPoint(tab_rect.right(), tab_rect.center().y()),
               QPoint(tab_rect.right() - 10, tab_rect.bottom()),
               QPoint(tab_rect.left(), tab_rect.bottom())]
        
        # Border
        p.setPen(QPen(QColor(col).darker(150), 3))
        p.setBrush(QColor(col))
        p.drawPolygon(QPolygon(pts))
        
        # Inner highlight for 3D effect
        inner_pts = [QPoint(pt.x() + 2, pt.y() + 2) for pt in pts[:-1]]
        p.setPen(QPen(QColor(col).lighter(120), 1))
        p.setBrush(Qt.NoBrush)
        p.drawPolygon(QPolygon(inner_pts))

    def _draw_bubble(self, painter, rect_widget, text, scale=1.0):
        """Draws printable message bubble to the right of highlight."""
        pad = int(6 * scale)
        max_w = int(180 * scale)
        metrics = painter.fontMetrics()
        wrapped = "\n".join(textwrap.wrap(text, width=40))
        br = metrics.boundingRect(0, 0, max_w, 1000, Qt.TextWordWrap, wrapped)
        bubble = QRect(rect_widget.right() + int(10 * scale),
                       rect_widget.top(),
                       br.width() + 2 * pad,
                       br.height() + 2 * pad)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QPen(QColor(ACCENT), int(2 * scale)))
        painter.drawRoundedRect(bubble, 8 * scale, 8 * scale)
        painter.setPen(QPen(Qt.black))
        painter.drawText(bubble.adjusted(pad, pad, -pad, -pad),
                         Qt.TextWordWrap, wrapped)

    # -------- painting override --------
    def paintEvent(self, event):
        # Call parent painting first
        super().paintEvent(event)
        
        # Only add annotation painting if we have rendered content
        if not self.pix:
            return
            
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)

        # Draw highlights
        for hl in self.highlights:
            if hl["page"] == self.page:
                qp.fillRect(self._pdf_to_widget(hl["pdf_rect"]), hl["color"])

        # Draw current selection
        if self.selecting and self.start_point:
            sel = QRect(self.start_point, self.end_point).normalized()
            cc = QColor(self.current_color)
            cc.setAlpha(100)
            qp.fillRect(sel, cc)

        # Draw tabs
        self.tab_rects.clear()
        for hl in self.highlights:
            if hl["page"] != self.page or not hl["tag"].get("printable", True): 
                continue
            wr = self._pdf_to_widget(hl["pdf_rect"])
            ty = max(self.render_rect.top(),
                     min(self.render_rect.bottom() - self.TAB_H,
                         wr.top() + (wr.height() - self.TAB_H) // 2))
            tx = self.render_rect.left() - self.TAB_W - 10  
            rect = QRect(tx, ty, self.TAB_W + 5, self.TAB_H)
            self.tab_rects.append((rect, hl))
            self._draw_tab(qp, rect, hl["color"])

    # -------- mouse events --------
    def mousePressEvent(self, e):
        # Check tab clicks first
        for r, hl in self.tab_rects:
            if r.contains(e.pos()):
                self._show_popup(hl["tag"], e.pos())
                return
                
        # Start selection if clicking in render area
        if e.button() == Qt.LeftButton and self.render_rect.contains(e.pos()):
            self.selecting = True
            self.start_point = self.end_point = e.pos()

    def mouseMoveEvent(self, e):
        if self.selecting: 
            self.end_point = e.pos()
            self.update()
        else: 
            self.hover_timer.start()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.selecting:
            self.selecting = False
            self.end_point = e.pos()
            self._new_highlight()

    # -------- NEW HIGHLIGHT - PROPER VERSION WITH TAG DIALOG --------
    def _new_highlight(self):
        """Create a new highlight from current selection"""
        print("_new_highlight called!")  # Debug
        
        if not self.start_point or not self.end_point:
            print("No start/end points")
            return
            
        sel = (QRect(self.start_point, self.end_point).normalized() & self.render_rect)
        if sel.width() < 5 or sel.height() < 5:
            print(f"Selection too small: {sel.width()}x{sel.height()}")
            return

        print(f"Selection OK: {sel}")

        # Convert to PDF coordinates
        p0 = self._widget_to_pdf(sel.topLeft())
        p1 = self._widget_to_pdf(sel.bottomRight())
        if not p0 or not p1:
            print("Failed to convert coordinates")
            return
            
        select_rect = fitz.Rect(p0.x, p0.y, p1.x, p1.y)

        # Get selected text - use simple method
        if self.doc:
            page = self.doc[self.page]
            selected_text = page.get_textbox(select_rect).strip()
        else:
            selected_text = ""
            
        if not selected_text:
            selected_text = "Selected area"

        print(f"Selected text: '{selected_text}'")

        # Show the proper TagDialog with presets
        try:
            from ui_components import TagDialog
            dlg = TagDialog(ACCENT, parent=self)
            
            # Pre-fill description with selected text
            dlg.desc_edit.setText(selected_text)
            
            print("Showing TagDialog...")
            result = dlg.exec()
            print(f"Dialog result: {result}")
            
            if result == QDialog.Accepted:
                tag_data = dlg.get_data()
                print(f"Tag data: {tag_data}")
                
                # Get color from tag data or use current color
                if 'color' in tag_data and tag_data['color'] in HIGHLIGHT_COLORS:
                    highlight_color = HIGHLIGHT_COLORS[tag_data['color']]
                    print(f"Using color: {tag_data['color']}")
                else:
                    highlight_color = self.current_color
                    print("Using default color")
                
                # Create highlight
                hl = dict(
                    page=self.page,
                    pdf_rect=select_rect,
                    color=highlight_color,
                    text=selected_text,
                    tag=tag_data,
                    id=len(self.highlights)
                )
                
                self.highlights.append(hl)
                self.highlight_created.emit(hl)
                self.update()
                self._auto_save()
                print("Highlight created successfully!")
            else:
                print("Dialog was cancelled")
                
        except Exception as e:
            print(f"Error showing TagDialog: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to simple message box
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Error", f"Could not show tag dialog: {e}")

    def _draw_manual_highlight(self, rect):
        """Fallback for manual highlighting when OCR fails"""
        # Get tag data first
        from dialogs import QuickPresetDialog
        dlg = QuickPresetDialog("Manual highlight", self)
        if dlg.exec() != QDialog.Accepted:
            return
            
        tag_data = dlg.get_tag_data()
        if not tag_data:
            return

        # Get color from tag data or use current color
        if 'color' in tag_data and tag_data['color'] in HIGHLIGHT_COLORS:
            highlight_color = HIGHLIGHT_COLORS[tag_data['color']]
        else:
            highlight_color = self.current_color

        # Create highlight without text
        hl = dict(
            page=self.page,
            pdf_rect=rect,
            color=highlight_color,
            text="Manual highlight",
            tag=tag_data,
            id=len(self.highlights)
        )
        
        self.highlights.append(hl)
        self.highlight_created.emit(hl)
        self.update()
        self._auto_save()

    # -------- popups --------
    def _show_popup(self, tag, pos_widget):
        """Show tag popup when clicking on tab"""
        gp = self.mapToGlobal(pos_widget + QPoint(10, 10))
        SleekTagPopup(tag, self).show_at(gp)

    def _show_toast(self, msg):
        """Show toast notification"""
        toast = ToastPopup(msg, self)
        toast.show_in(self.render_rect if self.render_rect.isValid() else self.rect())

    # -------- sidebar management --------
    def toggle_sidebar(self): 
        """Toggle sidebar visibility and remember the state"""
        is_visible = self.parent().sidebar.isVisible() if self.parent() else True
        if hasattr(self.parent(), 'sidebar'):
            self.parent().sidebar.setVisible(not is_visible)
            # Store the state so it doesn't auto-hide
            self.parent().sidebar_forced_open = not is_visible
    
    def open_presets(self): 
        from dialogs import PresetsDialog
        dlg = PresetsDialog(self)
        dlg.exec()
    def set_highlight_color(self, c): 
        self.current_color = c
        
    def set_preset(self, preset): 
        self.current_preset = preset
        
    def clear_preset(self): 
        self.current_preset = None
        
    def remove_highlight(self, hid):
        self.highlights = [h for h in self.highlights if h["id"] != hid]
        self.update()
        self._auto_save()

    # -------- export PDF (ALWAYS HIGH QUALITY WITH ANNOTATIONS) --------
    def export_pdf(self):
        """Export PDF with high-quality highlights and annotations"""
        if not self.doc: 
            return
        
        # Show loading screen
        from loading_screen import ExportLoadingScreen
        loading = ExportLoadingScreen(self)
        loading.start_loading(2000)  # 2 second loading
        
        loading.update_message("Choosing export location...")
        
        fn, _ = QFileDialog.getSaveFileName(self, "Export PDF 🌸",
                                            str(Path.home() / "Annotated_PDF.pdf"),
                                            "PDF Files (*.pdf)")
        if not fn: 
            loading.close()
            return

        loading.update_message("Creating beautiful PDF with annotations...")

        try:
            # Memory-safe document creation
            src = getattr(self.doc, 'name', None)
            if src and Path(src).exists():
                new_doc = fitz.open(src)
            else:
                # Handle in-memory documents safely
                doc_bytes = self.doc.write()
                new_doc = fitz.open(stream=doc_bytes, filetype="pdf")
            
            loading.update_message("Adding your highlights and annotations...")
            
            # Process highlights with memory management - ALWAYS HIGH QUALITY WITH ANNOTATIONS
            for i, hl in enumerate(self.highlights):
                try:
                    pg = new_doc[hl["page"]]
                    rect = fitz.Rect(hl["pdf_rect"])
                    col = hl["color"]
                    r, g, b, a = [c / 255.0 for c in col.getRgb()]

                    # Always draw high-quality highlight
                    pg.draw_rect(rect, color=None,
                                 fill=(r, g, b),
                                 fill_opacity=0.4,  # Slightly more visible
                                 overlay=True)
                    
                    # Draw highlight border for better visibility
                    pg.draw_rect(rect, color=(r * 0.7, g * 0.7, b * 0.7),
                                 fill=None, width=1.5, overlay=True)

                    # ALWAYS add annotations for printable tags
                    if hl["tag"].get("printable", True):
                        # Draw colored tab in left margin
                        tab_height = min(40, max(20, rect.height))
                        tab_x = max(10, rect.x0 - 15)  # Position tab to the left
                        tab = fitz.Rect(tab_x - 12, rect.y0, tab_x - 2, rect.y0 + tab_height)
                        
                        # Draw tab with stronger colors
                        pg.draw_rect(tab, color=(r * 0.8, g * 0.8, b * 0.8),
                                     fill=(r, g, b), fill_opacity=1.0, 
                                     width=1.5, overlay=True)
                        
                        # Add annotation bubble
                        try:
                            title = str(hl['tag'].get('title', 'Tagged'))
                            desc = str(hl['tag'].get('desc', ''))
                            
                            # Create annotation text
                            if title and desc:
                                bubble_text = f"{title}: {desc}"
                            elif title:
                                bubble_text = title
                            elif desc:
                                bubble_text = desc
                            else:
                                bubble_text = "Tagged"
                            
                            # Clean text for PDF compatibility
                            import re
                            bubble_text = re.sub(r'[^\w\s\-\.,!?\'"()]', '', bubble_text)
                            if len(bubble_text) > 80:
                                bubble_text = bubble_text[:77] + "..."
                            
                            if not bubble_text.strip():
                                bubble_text = "Tagged"
                            
                            # Position bubble in right margin or bottom
                            page_height = pg.rect.height
                            page_width = pg.rect.width
                            
                            # Try right margin first
                            bubble_x = min(page_width - 200, rect.x1 + 10)
                            bubble_y = rect.y0
                            bubble_w = min(180, page_width - bubble_x - 10)
                            bubble_h = 25
                            
                            # If it would go off page, put in bottom margin
                            if bubble_x + bubble_w > page_width - 10:
                                bubble_x = max(20, rect.x0)
                                bubble_y = page_height - 35
                                bubble_w = min(200, page_width - bubble_x - 20)
                            
                            bubble_rect = fitz.Rect(bubble_x, bubble_y,
                                                  bubble_x + bubble_w, bubble_y + bubble_h)
                            
                            # Draw bubble background with border
                            pg.draw_rect(bubble_rect, color=(0.3, 0.3, 0.3),
                                        fill=(0.95, 0.95, 0.95), fill_opacity=0.9,
                                        width=1, overlay=True)
                            
                            # Insert text in bubble
                            text_rect = fitz.Rect(bubble_rect.x0 + 4, bubble_rect.y0 + 3, 
                                                bubble_rect.x1 - 4, bubble_rect.y1 - 3)
                            pg.insert_textbox(text_rect,
                                              bubble_text,
                                              fontsize=8, fontname="helv",
                                              color=(0.1, 0.1, 0.1), align=0)
                            
                            # Draw connector line from highlight to bubble
                            if bubble_y != page_height - 35:  # Only if not in bottom margin
                                line_start = fitz.Point(rect.x1, rect.y0 + rect.height/2)
                                line_end = fitz.Point(bubble_x, bubble_y + bubble_h/2)
                                pg.draw_line(line_start, line_end, color=(0.5, 0.5, 0.5), width=1)
                        
                        except Exception as e:
                            print(f"Error creating annotation bubble: {e}")
                            # Continue without bubble if there's an error
                            pass
                        
                except Exception as e:
                    print(f"Error processing highlight {i}: {e}")
                    continue  # Skip problematic highlights

            loading.update_message("Saving your beautiful annotated PDF...")

            # Save with high quality settings
            try:
                new_doc.save(fn, garbage=4, deflate=True, clean=True)
            except Exception:
                # Fallback save
                new_doc.save(fn)
            finally:
                new_doc.close()
                new_doc = None
            
            loading.close()
            
            # Success message
            QMessageBox.information(self, "Export Complete! 🌸✨", 
                                  f"Your PDF has been exported with high-quality highlights and annotations!\n"
                                  f"🌺 Saved as: {Path(fn).name}\n\n"
                                  f"✨ Includes: Colored highlights, tabs, and annotation bubbles")
        except Exception as e:
            loading.close()
            QMessageBox.critical(self, "Export Error 😔", 
                                f"Sorry! Export failed: {str(e)}\n\n"
                                f"💡 Try:\n"
                                f"• Closing other programs\n"
                                f"• Saving to Desktop\n"
                                f"• Using a shorter filename")


class PDFPane(QWidget):
    """Main PDF pane widget that combines annotator with sidebar"""
    
    def __init__(self):
        super().__init__()
        self.viewer = PdfAnnotator()  # Use the new annotator instead
        self.sidebar = TagSidebar(self.viewer)
        self.sidebar_forced_open = False  # Track if user explicitly opened sidebar
        
        # Setup layout
        split = QSplitter(Qt.Horizontal)
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setWidget(self.viewer)
        sa.setStyleSheet(f"QScrollArea {{border:2px solid {ACCENT};border-radius:8px;}}")
        split.addWidget(sa)
        split.addWidget(self.sidebar)
        split.setSizes([1000, 320])
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(split)
        
    def load(self, p): 
        return self.viewer.load(p)
        
    def export(self): 
        self.viewer.export_pdf()
        
    def save_annotations(self): 
        return self.viewer.save_annotations()
        
    def load_annotations(self): 
        return self.viewer.load_annotations()
        
    def toggle_sidebar(self): 
        """Toggle sidebar and remember user's preference"""
        current_visible = self.sidebar.isVisible()
        new_visible = not current_visible
        self.sidebar.setVisible(new_visible)
        
        # If user is opening it, mark as forced open
        if new_visible:
            self.sidebar_forced_open = True
        else:
            self.sidebar_forced_open = False
        
    def ensure_sidebar_stays_open(self):
        """Ensure sidebar stays open if user explicitly opened it"""
        if self.sidebar_forced_open and not self.sidebar.isVisible():
            self.sidebar.setVisible(True)
        
    def open_presets(self): 
        from dialogs import PresetsDialog
        dlg = PresetsDialog(self)
        dlg.exec()
    
    # Zoom controls for PDFPane
    def zoom_in(self): 
        self.viewer.zoom_in()
        
    def zoom_out(self): 
        self.viewer.zoom_out()
        
    def reset_zoom(self): 
        self.viewer.reset_zoom()
        
    def fit_to_width(self): 
        self.viewer.fit_to_width()