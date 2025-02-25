from pathlib import Path
from typing import List, Union
import fitz  # PyMuPDF for PDF handling
from docx import Document  # python-docx for Word documents
from PIL import Image, ImageDraw, ImageFont  # Pillow for image handling
import os

class DiplomaGenerator:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png']
        self.template_path = None
        self.template_format = None
        
        # Remove AI initialization for now
        # self.text_detector = pipeline("object-detection", model="microsoft/layoutlm-base-uncased")

    def load_template(self, template_path: Union[str, Path]) -> None:
        """Load the diploma template in any supported format"""
        template_path = Path(template_path)
        if not template_path.suffix.lower() in self.supported_formats:
            raise ValueError(f"Unsupported file format. Supported formats: {self.supported_formats}")
        
        self.template_path = template_path
        self.template_format = template_path.suffix.lower()

    def load_names(self, names_path: Union[str, Path]) -> List[str]:
        """Load names from a text file (one name per line)"""
        with open(names_path, 'r', encoding='utf-8') as f:
            return [name.strip() for name in f.readlines() if name.strip()]

    def detect_placeholder(self) -> str:
        """Use AI to detect potential name placeholder in the template"""
        # Implementation depends on the file format
        if self.template_format in ['.jpg', '.jpeg', '.png']:
            return self._detect_placeholder_image()
        elif self.template_format == '.pdf':
            return self._detect_placeholder_pdf()
        else:  # Word documents
            return self._detect_placeholder_word()

    def generate_diplomas(self, names: List[str], output_dir: Union[str, Path], 
                         placeholder: str, output_format: str = 'pdf') -> List[Path]:
        """Generate individual diplomas and return list of generated file paths"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        generated_files = []
        for name in names:
            output_path = output_dir / f"diploma_{name.replace(' ', '_')}.{output_format}"
            self._generate_single_diploma(name, placeholder, output_path)
            generated_files.append(output_path)
            
        return generated_files

    def _detect_placeholder_image(self) -> str:
        """Detect placeholder in image formats using OCR and AI"""
        image = Image.open(self.template_path)
        # Use pytesseract for OCR
        text = pytesseract.image_to_string(image)
        # Use AI to identify likely placeholder
        # Implementation details here

    def _detect_placeholder_pdf(self) -> str:
        """Detect placeholder in PDF format"""
        # Implementation using PyMuPDF

    def _detect_placeholder_word(self) -> str:
        """Detect placeholder in Word documents"""
        # Implementation using python-docx

    def _generate_single_diploma(self, name: str, placeholder: str, output_path: Path) -> None:
        """Generate a single diploma based on the template format"""
        if self.template_format in ['.jpg', '.jpeg', '.png']:
            self._generate_from_image(name, placeholder, output_path)
        elif self.template_format == '.pdf':
            self._generate_from_pdf(name, placeholder, output_path)
        else:  # Word documents
            self._generate_from_word(name, placeholder, output_path)

    def _generate_from_image(self, name: str, placeholder: str, output_path: Path) -> None:
        """Generate diploma from image template"""
        with Image.open(self.template_path) as img:
            # Create a copy to work with
            new_img = img.copy()
            draw = ImageDraw.Draw(new_img)
            
            # Basic implementation - you might want to adjust font size and position
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except OSError:
                font = ImageFont.load_default()
                
            # Center the name (basic implementation)
            w, h = img.size
            text_bbox = draw.textbbox((0, 0), name, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            x = (w - text_w) / 2
            y = (h - text_h) / 2
            
            draw.text((x, y), name, fill='black', font=font)
            new_img.save(output_path)

    def _generate_from_pdf(self, name: str, placeholder: str, output_path: Path) -> None:
        """Generate diploma from PDF template"""
        doc = fitz.open(self.template_path)
        for page in doc:
            text = page.get_text()
            if placeholder in text:
                text = text.replace(placeholder, name)
                page.insert_text((100, 100), text)  # Adjust position as needed
        doc.save(output_path)
        doc.close()

    def _generate_from_word(self, name: str, placeholder: str, output_path: Path) -> None:
        """Generate diploma from Word template"""
        doc = Document(self.template_path)
        for paragraph in doc.paragraphs:
            if placeholder in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder, name)
        doc.save(output_path) 