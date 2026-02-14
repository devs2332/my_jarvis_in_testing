"""
Screen reading capabilities using OCR.

Captures screen content and extracts text using Tesseract OCR.
"""

import logging
from PIL import Image
import mss
import pytesseract
import os

logger = logging.getLogger(__name__)


class ScreenReader:
    """
    Reads text from screen using OCR.
    
    Captures screenshots and extracts text content for accessibility
    and automation purposes.
    """
    
    def __init__(self):
        """Initialize the screen reader."""
        logger.info("🖥️ Screen Reader initialized")
        # Set tesseract path if needed (Windows)
        # Uncomment and adjust path if tesseract not in PATH
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def capture_screen(self, monitor_number=1):
        """
        Capture a screenshot of specified monitor.
        
        Args:
            monitor_number (int): Monitor to capture (1-indexed, 0 for all)
            
        Returns:
            PIL.Image: Screenshot image
        """
        try:
            with mss.mss() as sct:
                if monitor_number == 0:
                    # Capture all monitors
                    monitor = sct.monitors[0]
                else:
                    # Capture specific monitor
                    monitor = sct.monitors[monitor_number]
                
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                
                logger.info(f"✅ Captured screen {monitor_number}")
                return img
                
        except Exception as e:
            logger.error(f"❌ Screen capture error: {e}")
            return None
    
    def read_screen(self, monitor_number=1):
        """
        Capture screen and extract text using OCR.
        
        Args:
            monitor_number (int): Monitor to read (1-indexed)
            
        Returns:
            str: Extracted text from screen
        """
        try:
            logger.info(f"📖 Reading screen {monitor_number}...")
            
            # Capture screenshot
            img = self.capture_screen(monitor_number)
            if img is None:
                return "Error: Could not capture screen"
            
            # Extract text using OCR
            text = pytesseract.image_to_string(img)
            
            if text.strip():
                logger.info(f"✅ Extracted {len(text)} characters from screen")
                return text.strip()
            else:
                logger.warning("⚠️ No text found on screen")
                return "No text detected on screen"
                
        except Exception as e:
            logger.error(f"❌ OCR error: {e}")
            return f"Error reading screen: {str(e)}"
    
    def read_region(self, x, y, width, height):
        """
        Read text from specific screen region.
        
        Args:
            x (int): Left coordinate
            y (int): Top coordinate
            width (int): Region width
            height (int): Region height
            
        Returns:
            str: Extracted text from region
        """
        try:
            logger.info(f"📖 Reading region ({x}, {y}, {width}, {height})...")
            
            with mss.mss() as sct:
                monitor = {
                    "top": y,
                    "left": x,
                    "width": width,
                    "height": height
                }
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            
            # Extract text
            text = pytesseract.image_to_string(img)
            
            if text.strip():
                logger.info(f"✅ Extracted {len(text)} characters from region")
                return text.strip()
            else:
                return "No text detected in region"
                
        except Exception as e:
            logger.error(f"❌ Region OCR error: {e}")
            return f"Error reading region: {str(e)}"
    
    def save_screenshot(self, filepath, monitor_number=1):
        """
        Save screenshot to file.
        
        Args:
            filepath (str): Path to save screenshot
            monitor_number (int): Monitor to capture
            
        Returns:
            str: Success message or error
        """
        try:
            img = self.capture_screen(monitor_number)
            if img is None:
                return "Error: Could not capture screen"
            
            img.save(filepath)
            logger.info(f"✅ Screenshot saved to {filepath}")
            return f"Screenshot saved to {filepath}"
            
        except Exception as e:
            logger.error(f"❌ Save screenshot error: {e}")
            return f"Error saving screenshot: {str(e)}"
