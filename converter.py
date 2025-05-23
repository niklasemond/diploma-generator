import subprocess
import os
import time
import logging
from pathlib import Path
from typing import Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_single_doc_to_pdf(input_path: str, output_path: str, port: int, is_pdf: bool = False) -> None:
    """Convert a single document to PDF or Word using LibreOffice"""
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Build the command
        if is_pdf:
            # For PDF to Word conversion
            cmd = [
                'soffice',
                '--headless',
                '--convert-to', 'docx',
                '--outdir', os.path.dirname(output_path),
                input_path
            ]
        else:
            # For Word to PDF conversion
            cmd = [
                'soffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', os.path.dirname(output_path),
                input_path
            ]
        
        # Run the conversion
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for the conversion to complete
        stdout, stderr = process.communicate(timeout=30)
        
        if process.returncode != 0:
            raise Exception(f"Conversion failed: {stderr.decode()}")
        
        # Wait a moment to ensure the file is written
        time.sleep(1)
        
        # Verify the output file exists
        if not os.path.exists(output_path):
            raise Exception(f"Output file was not created: {output_path}")
        
        logger.info(f"Successfully converted {input_path} to {output_path}")
        
    except Exception as e:
        logger.error(f"Error converting document: {str(e)}")
        raise 