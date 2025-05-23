from pathlib import Path
from typing import List, Union
import fitz  # PyMuPDF for PDF handling
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiplomaGenerator:
    def __init__(self):
        self.template_path = None

    def load_template(self, template_path: Union[str, Path]) -> None:
        """Load the diploma template in PDF format"""
        template_path = Path(template_path)
        if not template_path.suffix.lower() == '.pdf':
            raise ValueError("Only PDF templates are supported")
        
        self.template_path = template_path
        logger.info(f"Template loaded: {template_path}")

    def load_names(self, names_path: Union[str, Path]) -> List[str]:
        """Load names from a text file (one name per line)"""
        with open(names_path, 'r', encoding='utf-8') as f:
            names = [name.strip() for name in f.readlines() if name.strip()]
            logger.info(f"Loaded {len(names)} names from {names_path}")
            return names

    def generate_diplomas(self, names: List[str], output_dir: Union[str, Path], 
                         placeholder: str) -> List[Path]:
        """Generate individual diplomas and return list of generated file paths"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        generated_files = []
        for name in names:
            try:
                output_path = output_dir / f"diploma_{name.replace(' ', '_')}.pdf"
                self._generate_single_diploma(name, placeholder, output_path)
                generated_files.append(output_path)
                logger.info(f"Generated diploma for {name}")
            except Exception as e:
                logger.error(f"Failed to generate diploma for {name}: {str(e)}")
                continue
            
        return generated_files

    def _generate_single_diploma(self, name: str, placeholder: str, output_path: Path) -> None:
        """Generate a single diploma by replacing the placeholder with the name"""
        try:
            # Open the source PDF
            doc = fitz.open(self.template_path)
            
            # Create a new PDF document
            new_doc = fitz.open()
            
            # Copy pages from source to new document
            new_doc.insert_pdf(doc)
            
            # Process each page
            for page in new_doc:
                # Get all text instances
                text_instances = page.search_for(placeholder)
                
                # Replace each instance of the placeholder
                for inst in text_instances:
                    # First remove the old text by drawing a white rectangle over it
                    page.draw_rect(inst, color=fitz.utils.getColor('white'), fill=fitz.utils.getColor('white'))
                    
                    # Insert the new name at the same position
                    page.insert_text(
                        (inst[0], inst[1]),  # Use the same position as the placeholder
                        name,
                        fontsize=12,  # Default font size
                        color=fitz.utils.getColor('black')
                    )
            
            # Save the modified document
            new_doc.save(str(output_path))
            
            # Close both documents
            new_doc.close()
            doc.close()
            
            # Verify the file was created and is readable
            if not output_path.exists():
                raise ValueError(f"Failed to save document to {output_path}")
            
            # Try to open the file to verify it's valid
            try:
                test_doc = fitz.open(str(output_path))
                if test_doc.page_count == 0:
                    raise ValueError("Generated document has no pages")
                test_doc.close()
            except Exception as e:
                raise ValueError(f"Generated document is not valid: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error generating document from PDF: {str(e)}")
            # Clean up any potentially corrupted files
            if output_path.exists():
                try:
                    output_path.unlink()
                except:
                    pass
            raise 