from celery import Celery
from pathlib import Path
import os
from diploma_generator import DiplomaGenerator

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task(bind=True, max_retries=3)
def convert_document(self, docx_path: str, pdf_path: str) -> dict:
    """Convert a single document with retry capability"""
    try:
        generator = DiplomaGenerator()
        generator.convert_to_pdf(Path(docx_path), Path(pdf_path))
        return {
            'status': 'success',
            'file': pdf_path,
            'message': f'Successfully converted {os.path.basename(docx_path)}'
        }
    except Exception as e:
        try:
            self.retry(countdown=5)  # Retry after 5 seconds
        except self.MaxRetriesExceededError:
            return {
                'status': 'error',
                'file': docx_path,
                'message': f'Failed to convert {os.path.basename(docx_path)}: {str(e)}'
            }

@celery.task
def cleanup_files(paths: list) -> None:
    """Clean up temporary files after conversion"""
    for path in paths:
        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
        except Exception as e:
            print(f"Error cleaning up {path}: {e}") 