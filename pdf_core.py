# pdf_core.py – Core PDF Display and Navigation
# --------------------------------------------------------------------

import sys, io
from pathlib import Path
import fitz       # PyMuPDF

from PySide6.QtCore import (
    Qt, QRect, QPoint, QTimer
)
from PySide6.QtGui import (
    QPainter, QColor, QPixmap, QImage, QCursor
)
from PySide6.QtWidgets import (
    QWidget, QLabel, QFileDialog, QMessageBox
)

from ui_components import ACCENT

# ───────────────────────── Core PDF Display ─────────────────────────
class PdfCore(QLabel):
    """Core PDF display without tagging - handles zoom, navigation, rendering"""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"background:#1a1a1a;border:2px solid {ACCENT};border-radius:8px")
        self.setMinimumSize(600, 800); self.setMouseTracking(True)

        self.doc = None; self.page = 0; self.zoom = 2.8; self.pix = None
        self.render_rect = QRect()
        self.text_blocks = []
        self.hover_timer = QTimer(singleShot=True, interval=50, timeout=self._hover)

    # -------- file ops --------
    def load(self, p: str):
        try:
            self.doc = fitz.open(p)
            self.page = 0
            self.original_path = p
            self._render()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return False

    def _render(self):
        if not self.doc: return
        pg = self.doc[self.page]
        pm = pg.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom), alpha=False)
        self.pix = QPixmap.fromImage(QImage(pm.samples, pm.width, pm.height,
                                            pm.stride, QImage.Format_RGB888))
        self._cache_blocks()
        self.update()

    def _cache_blocks(self):
        """Cache text blocks for text detection overlay"""
        self.text_blocks.clear()
        if not self.doc: return
        for b in self.doc[self.page].get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["text"].strip():
                        self.text_blocks.append({"rect": fitz.Rect(s["bbox"]),
                                                 "text": s["text"]})

    # -------- coordinate helpers --------
    def _widget_to_pdf(self, pt):
        if not self.render_rect.contains(pt): return None
        relx = (pt.x() - self.render_rect.left()) / self.render_rect.width()
        rely = (pt.y() - self.render_rect.top())  / self.render_rect.height()
        pg = self.doc[self.page].rect
        return fitz.Point(relx * pg.width, rely * pg.height)

    def _pdf_to_widget(self, r):
        if not self.doc: return QRect()
        pg = self.doc[self.page].rect
        x = r.x0 / pg.width  * self.render_rect.width()  + self.render_rect.left()
        y = r.y0 / pg.height * self.render_rect.height() + self.render_rect.top()
        w = r.width  / pg.width  * self.render_rect.width()
        h = r.height / pg.height * self.render_rect.height()
        return QRect(int(x), int(y), int(w), int(h))

    # -------- painting --------
    def paintEvent(self, _):
        if not self.pix: return super().paintEvent(_)
        qp = QPainter(self); qp.setRenderHint(QPainter.Antialiasing)
        ws, ps = self.size(), self.pix.size()
        sc = min(ws.width() / ps.width(), ws.height() / ps.height())
        w, h = int(ps.width() * sc), int(ps.height() * sc)
        x0, y0 = (ws.width() - w) // 2, (ws.height() - h) // 2
        self.render_rect = QRect(x0, y0, w, h)
        qp.drawPixmap(self.render_rect, self.pix)

        # Draw text detection overlay if enabled
        if hasattr(self, 'show_text_detection') and self.show_text_detection:
            self._draw_text_overlay(qp)

    def _draw_text_overlay(self, painter):
        """Draw text detection overlay showing detected text blocks (improved)"""
        # Draw semi-transparent filled rectangles like in the example
        painter.setPen(QColor(0, 255, 0, 200))  # Bright green border
        painter.setBrush(QColor(0, 255, 0, 60))   # Semi-transparent green fill
        
        for block in self.text_blocks:
            widget_rect = self._pdf_to_widget(block["rect"])
            if widget_rect.isValid() and widget_rect.width() > 2 and widget_rect.height() > 2:
                # Draw filled rectangle (highlight style)
                painter.drawRect(widget_rect)
                
                # Optional: Draw text preview for debugging
                if widget_rect.width() > 50:  # Only for larger blocks
                    painter.setPen(QColor(255, 255, 255, 180))  # White text
                    text_preview = block["text"][:20] + "..." if len(block["text"]) > 20 else block["text"]
                    painter.drawText(widget_rect.adjusted(2, 2, -2, -2), Qt.AlignLeft | Qt.AlignTop, text_preview)
                    painter.setPen(QColor(0, 255, 0, 200))  # Reset pen

    # -------- zoom controls (FIXED) --------
    def zoom_in(self):
        if self.zoom < 8.0:
            self.zoom += 0.5
            self._render()
            return True
        return False
    
    def zoom_out(self):
        if self.zoom > 0.5:
            self.zoom -= 0.5
            self._render()
            return True
        return False
    
    def reset_zoom(self):
        self.zoom = 2.8
        self._render()
    
    def fit_to_width(self):
        if not self.doc: return
        pg = self.doc[self.page]
        available_width = self.width() - 40
        page_width = pg.rect.width
        new_zoom = available_width / page_width
        self.zoom = max(0.5, min(8.0, new_zoom))
        self._render()

    # -------- navigation --------
    def goto(self, n): 
        if self.doc and 0 <= n < len(self.doc):
            self.page = n
            self._render()
            # Update main window page display
            if self.parent() and hasattr(self.parent().parent(), '_update_page_display'):
                self.parent().parent()._update_page_display()
    jump_to_page = goto

    # -------- wheel event (zoom) --------
    def wheelEvent(self, e):
        if not self.doc: return
        
        # Check if Ctrl is held for zoom, otherwise navigate pages
        if e.modifiers() & Qt.ControlModifier:
            delta = e.angleDelta().y()
            old_zoom = self.zoom
            
            if delta > 0:
                success = self.zoom_in()
            else:
                success = self.zoom_out()
            
            if success:
                e.accept()
            else:
                e.ignore()
        else:
            # Normal page navigation
            self.goto(self.page + 1 if e.angleDelta().y() < 0 else self.page - 1)
            e.accept()

    # -------- hover cursor --------
    def _hover(self):
        pt = self.mapFromGlobal(QCursor.pos())
        pdf = self._widget_to_pdf(pt)
        self.setCursor(Qt.IBeamCursor if pdf and any(b["rect"].contains(pdf)
                                                     for b in self.text_blocks)
                       else Qt.ArrowCursor)

    # -------- text detection toggle --------
    def toggle_text_detection(self, enabled):
        """Toggle text detection overlay"""
        self.show_text_detection = enabled
        self.update()

    def get_text_at_point(self, widget_point):
        """Get text at a specific widget point (improved)"""
        pdf_point = self._widget_to_pdf(widget_point)
        if not pdf_point: 
            return ""
        
        # Find the text block that contains this point
        for block in self.text_blocks:
            if block["rect"].contains(pdf_point):
                return block["text"].strip()
        return ""