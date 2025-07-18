# pdf_viewer.py – PDF Viewer Main Module (Updated)
# --------------------------------------------------------------------
# This file now imports from the split modules for better organization

# Import the main classes from the split files
from pdf_core import PdfCore
from pdf_annotator import PdfAnnotator, PDFPane

# Re-export for backwards compatibility
__all__ = ['PdfCore', 'PdfAnnotator', 'PDFPane', 'PdfViewer']

# Alias for backwards compatibility
PdfViewer = PdfAnnotator