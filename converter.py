import subprocess
import logging
from pathlib import Path
from typing import Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_single_doc_to_pdf(docx_path: Union[str, Path], pdf_path: Union[str, Path], port: int) -> None:
    """Convert a single Word document to PDF using soffice"""
    try:
        logger.info(f"Converting {docx_path} to PDF")
        
        # Try conversion with specific port
        result = subprocess.run(
            ['soffice', 
             f'--accept=socket,host=127.0.0.1,port={port};urp;StarOffice.ServiceManager', 
             '--headless', 
             '--convert-to', 'pdf', 
             '--outdir', str(Path(pdf_path).parent), 
             str(docx_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.warning(f"Conversion failed on port {port}: {result.stderr}")
            raise ValueError(f"Conversion failed: {result.stderr}")
            
        logger.info(f"Successfully converted {docx_path} to PDF using port {port}")
        
    except Exception as e:
        error_msg = f"Error converting {docx_path} to PDF: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) 