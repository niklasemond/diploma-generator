import os
import requests
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_font():
    """Download the Montessori font and save it to the fonts directory"""
    # Create fonts directory if it doesn't exist
    fonts_dir = Path('fonts')
    fonts_dir.mkdir(exist_ok=True)
    
    font_path = fonts_dir / 'Montessori.ttf'
    
    # If font already exists, skip download
    if font_path.exists():
        logger.info("Montessori font already exists in fonts directory")
        return
    
    # URL for the Montessori font
    # Note: This is a placeholder URL. You'll need to replace it with the actual URL
    # where the font can be downloaded from
    font_url = "https://example.com/Montessori.ttf"  # Replace with actual URL
    
    try:
        logger.info("Downloading Montessori font...")
        response = requests.get(font_url)
        response.raise_for_status()
        
        # Save the font file
        with open(font_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Successfully downloaded Montessori font to {font_path}")
        
    except Exception as e:
        logger.error(f"Failed to download font: {e}")
        raise

if __name__ == '__main__':
    download_font() 