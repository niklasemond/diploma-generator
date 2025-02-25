from celery import Celery
from pathlib import Path
import os
from converter import convert_single_doc_to_pdf
import random

# Configure Celery with Redis as both broker and result backend
celery = Celery('tasks',
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/1')  # Use different DB for results

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

SOFFICE_PORTS = list(range(8100, 8103))  # 3 ports for conversion

@celery.task(bind=True, max_retries=3)
def convert_document(self, docx_path: str, pdf_path: str) -> dict:
    """Convert a single document with retry capability"""
    try:
        port = random.choice(SOFFICE_PORTS)
        convert_single_doc_to_pdf(docx_path, pdf_path, port)
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