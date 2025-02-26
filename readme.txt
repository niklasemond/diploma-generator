Diploma Generator

A web application that generates personalized diplomas from a template. Upload a diploma template and a list of names, and receive a zip file containing individual diplomas for each person.

Features
- Supports multiple template formats (PDF, Word, JPG, PNG)
- Easy-to-use web interface
- Bulk diploma generation
- Sequential PDF conversion for reliability
- Automatic file cleanup
- Secure file handling
- Downloads as a convenient zip file

Getting Started

Prerequisites
- Python 3.11 or higher
- Docker (optional, for containerized deployment)
- Redis (for task queue)
- LibreOffice (for PDF conversion)

Local Development Setup

1. Clone the repository
git clone https://github.com/YOUR_USERNAME/diploma-generator.git
cd diploma-generator

2. Create and activate a virtual environment
python -m venv env
source env/bin/activate # On Windows: env\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Install system dependencies
sudo apt-get install libreoffice libreoffice-writer redis-server

5. Start Redis
redis-server

6. Start Celery worker
celery -A tasks worker --loglevel=info --concurrency=1

7. Run the application
python app.py

The application will be available at http://localhost:8080

Docker Deployment

1. Build the Docker image
docker build -t diploma-generator .

2. Run the container
docker run -p 8080:8080 diploma-generator

Usage

1. Prepare your files:
   - A diploma template (PDF, Word, JPG, or PNG format)
   - A text file containing names (one name per line)

2. Access the web interface and:
   - Upload your diploma template
   - Upload your names file
   - Specify the placeholder text that will be replaced with names

3. For Word to PDF conversion:
   - Upload Word documents (.docx)
   - Files are converted sequentially for reliability
   - Each conversion has automatic retries
   - Download converted PDFs as a zip file

Technical Details

The application uses:
- Flask for the web framework
- Celery for task queue management
- Redis for message broker and result backend
- LibreOffice for Word to PDF conversion
- PyMuPDF for PDF processing
- python-docx for Word document handling
- Pillow for image processing

Architecture:
- Sequential processing to prevent resource conflicts
- Single LibreOffice instance for stability
- Automatic process cleanup between conversions
- Task queue with retry capability
- Resource limits for better reliability

Security Features:
- Secure filename handling
- Maximum file size limit (16MB)
- Process isolation
- Resource cleanup

Troubleshooting

1. File Upload Issues
   - Ensure file size is under 16MB
   - Check if file format is supported
   - Verify file is not corrupted

2. PDF Conversion Issues
   - Check if LibreOffice is installed correctly
   - Ensure enough system resources
   - Look for conversion timeout errors
   - Check Redis connection
   - Verify LibreOffice process status

3. Download Issues
   - Check if browser allows downloads
   - Ensure enough disk space
   - Verify zip file is not corrupted

For more help, please open an issue on the GitHub repository.

Contributing
1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments
- Flask web framework
- PyMuPDF for PDF processing
- python-docx for Word document handling
- Pillow for image processing