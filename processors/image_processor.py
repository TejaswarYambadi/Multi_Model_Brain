import os
from pathlib import Path
from PIL import Image
from utils.gemini_client import GeminiClient

class ImageProcessor:
    """Handles processing of image files using Gemini Vision"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    def process(self, file_path: str) -> str:
        """
        Process an image file and extract content description
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Image analysis and description
        """
        try:
            # Verify file exists and is valid image
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Image file not found: {file_path}")
            
            # Convert to JPEG if needed (Gemini works best with JPEG)
            processed_path = self._ensure_jpeg(file_path)
            
            try:
                # Use Gemini to analyze the image
                description = self.gemini_client.analyze_image(processed_path)
                
                # Add file metadata to description
                filename = Path(file_path).name
                return f"Image: {filename}\n\nAnalysis:\n{description}"
                
            finally:
                # Clean up temporary file if it was created
                if processed_path != file_path and os.path.exists(processed_path):
                    os.unlink(processed_path)
                    
        except Exception as e:
            raise Exception(f"Error processing image {file_path}: {str(e)}")
    
    def _ensure_jpeg(self, file_path: str) -> str:
        """
        Convert image to JPEG format if needed
        
        Args:
            file_path: Path to original image
            
        Returns:
            Path to JPEG image (same as input if already JPEG)
        """
        file_extension = Path(file_path).suffix.lower()
        
        # If already JPEG, return as-is
        if file_extension in ['.jpg', '.jpeg']:
            return file_path
        
        try:
            # Open and convert to JPEG
            with Image.open(file_path) as img:
                # Convert to RGB if necessary (PNG with transparency, etc.)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as JPEG
                temp_path = file_path.rsplit('.', 1)[0] + '_temp.jpg'
                img.save(temp_path, 'JPEG', quality=95)
                return temp_path
                
        except Exception as e:
            raise Exception(f"Error converting image to JPEG: {str(e)}")
