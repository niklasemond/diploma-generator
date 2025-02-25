Diploma Generator

A web application that generates personalized diplomas from a template. Upload a diploma template and a list of names, and receive a zip file containing individual diplomas for each person.

Features
 - Supports multiple template formats (PDF, Word, JPG, PNG)
 - Easy-to-use web interface
 - Bulk diploma generation
 - Automatic file cleanup
 - Secure file handling
 - Downloads as a convenient zip file

Getting Started

Prerequisites
- Python 3.11 or higher
- Docker (optional, for containerized deployment)

Local Development Setup

1. Clone the repository
git clone https://github.com/YOUR_USERNAME/diploma-generator.git
cd diploma-generator
2. Create and activate a virtual environment
python -m venv env
source env/bin/activate # On Windows: env\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Run the application
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
- Click "Generate Diplomas"
Download the generated zip file containing all diplomas

File Format Support
Templates:
- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- Images (.jpg, .jpeg, .png)
Names List:
- Text file (.txt) with one name per line

Environment Variables
- UPLOAD_FOLDER: Directory for temporary upload storage (default: 'uploads')
- OUTPUT_FOLDER: Directory for generated files (default: 'output')
- PORT: Application port (default: 8080)

Deployment
This application can be deployed on any platform that supports Docker containers. Recommended platforms:
- Render
- Heroku
- Google Cloud Run
- AWS Elastic Beanstalk

Security
- File uploads are validated for type and size
- Temporary files are automatically cleaned up
Secure filename handling
Maximum file size limit (16MB)

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

Technical Details
The application uses a combination of libraries to handle different file formats:
- PDF processing: PyMuPDF (fitz)
- Word documents: python-docx
- Images: Pillow (PIL)

The web interface is built with:
- Flask for the backend
- Bootstrap 5 for the frontend
- Vanilla JavaScript for form handling and file uploads

Troubleshooting
Common issues:
1. File Upload Issues
- Ensure file size is under 16MB
- Check if file format is supported
- Verify file is not corrupted

2. Processing Issues
- Ensure placeholder text matches exactly
- Check if template file is properly formatted
Verify names file has proper line endings

3. Download Issues
- Check if browser allows downloads
- Ensure enough disk space for generated files
- Verify zip file is not corrupted

For more help, please open an issue on the GitHub repository.