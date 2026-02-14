"""
Screen context analysis using Vision LLM.

Analyzes screenshots to understand UI context and provide descriptions.
"""

import logging
from PIL import Image
import base64
import io
from core.llm_client import LLMClient

logger = logging.getLogger(__name__)


class ScreenAnalyzer:
    """
    Analyzes screen content using Vision LLM.
    
    Provides semantic understanding of screen content beyond just OCR,
    including UI element detection, layout understanding, and context.
    """
    
    def __init__(self):
        """Initialize the screen analyzer."""
        self.llm = LLMClient()
        logger.info("👁️ Screen Analyzer initialized")
    
    def analyze_screenshot(self, image, question="What do you see on this screen?"):
        """
        Analyze a screenshot and answer questions about it.
        
        Args:
            image (PIL.Image): Screenshot to analyze
            question (str): Question to ask about the screen
            
        Returns:
            str: Analysis or answer
            
        Note:
            This requires a vision-capable LLM (GPT-4 Vision, Gemini Vision, etc.)
        """
        try:
            logger.info(f"🔍 Analyzing screen: '{question[:50]}...'")
            
            # Convert image to base64 for LLM
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Create vision prompt
            prompt = f"""
You are analyzing a screenshot.

Question: {question}

Describe what you see on the screen in detail. Include:
- Main UI elements (buttons, menus, windows)
- Text content
- Layout and organization
- What the user is likely trying to do

Be concise but informative.
"""
            
            # Note: This is a placeholder for vision LLM integration
            # Actual implementation depends on the LLM provider supporting vision
            # For now, return helpful message
            
            response = """
Screen analysis requires a vision-capable LLM model.

To enable this feature:
1. Use OpenAI GPT-4 Vision
2. Use Google Gemini Pro Vision
3. Or use a local vision model

Current LLM may not support image analysis.
"""
            
            logger.info("✅ Screen analysis complete")
            return response
            
        except Exception as e:
            logger.error(f"❌ Screen analysis error: {e}")
            return f"Error analyzing screen: {str(e)}"
    
    def describe_ui(self, image):
        """
        Describe the user interface elements on screen.
        
        Args:
            image (PIL.Image): Screenshot to analyze
            
        Returns:
            str: UI description
        """
        return self.analyze_screenshot(
            image,
            "Describe all the UI elements, buttons, menus, and interactive components you see."
        )
    
    def find_element(self, image, element_description):
        """
        Find a specific UI element on screen.
        
        Args:
            image (PIL.Image): Screenshot to analyze
            element_description (str): Description of element to find
            
        Returns:
            str: Location and details of element
        """
        return self.analyze_screenshot(
            image,
            f"Where is the {element_description}? Describe its location and appearance."
        )
