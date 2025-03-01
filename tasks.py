import time
from celery import Celery
from pathlib import Path
import os
from converter import convert_single_doc_to_pdf
import random

# Configure Celery with Redis as both broker and result backend
celery = Celery('tasks',
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/1')

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_time_limit=180,  # 3 minutes max per task
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks
    worker_prefetch_multiplier=1,  # Only prefetch one task at a time
)

# Use a single port for conversion to prevent conflicts
SOFFICE_PORT = 8100

@celery.task(bind=True, max_retries=3)
def convert_document(self, docx_path: str, pdf_path: str) -> dict:
    """Convert a single document with retry capability"""
    try:
        # Kill any existing soffice processes before starting
        os.system("pkill soffice || true")
        time.sleep(1)  # Wait for process to clean up
        
        convert_single_doc_to_pdf(docx_path, pdf_path, SOFFICE_PORT)
        return {
            'status': 'success',
            'file': pdf_path,
            'message': f'Successfully converted {os.path.basename(docx_path)}'
        }
    except Exception as e:
        try:
            # Kill soffice process before retry
            os.system("pkill soffice || true")
            time.sleep(2)  # Give more time for cleanup before retry
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