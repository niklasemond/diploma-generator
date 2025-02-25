from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from diploma_generator import DiplomaGenerator
import shutil
import zipfile

app = Flask(__name__)

# Use environment variables for configuration
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.environ.get('OUTPUT_FOLDER', 'output')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png'}
ALLOWED_WORD_EXTENSIONS = {'.docx', '.doc'}

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def allowed_word_file(filename):
    """Check if the file is a Word document"""
    return os.path.splitext(filename)[1].lower() in ALLOWED_WORD_EXTENSIONS

def cleanup_files(template_path, names_path, zip_path):
    """Clean up temporary files"""
    try:
        if os.path.exists(template_path):
            os.remove(template_path)
        if os.path.exists(names_path):
            os.remove(names_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)
    except Exception as e:
        app.logger.error(f"Error cleaning up files: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'template' not in request.files:
        return jsonify({'error': 'No template file provided'}), 400
    
    if 'names' not in request.files:
        return jsonify({'error': 'No names file provided'}), 400

    template_file = request.files['template']
    names_file = request.files['names']
    placeholder = request.form.get('placeholder', '[NAME]')
    output_format = request.form.get('output_format', 'docx')  # Default to docx

    if template_file.filename == '':
        return jsonify({'error': 'No template selected'}), 400
    
    if names_file.filename == '':
        return jsonify({'error': 'No names file selected'}), 400

    if not allowed_file(template_file.filename):
        return jsonify({'error': 'Invalid template file format'}), 400

    try:
        # Ensure directories exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

        # Save uploaded files
        template_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                   secure_filename(template_file.filename))
        names_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                secure_filename(names_file.filename))
        
        template_file.save(template_path)
        names_file.save(names_path)

        # Generate diplomas
        generator = DiplomaGenerator()
        generator.load_template(template_path)
        names = generator.load_names(names_path)
        
        output_dir = app.config['OUTPUT_FOLDER']
        generated_files = generator.generate_diplomas(
            names, 
            output_dir, 
            placeholder,
            output_format='docx'  # Force Word format
        )

        # Create zip file
        zip_path = os.path.join(output_dir, 'diplomas.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in generated_files:
                zipf.write(file_path, os.path.basename(file_path))

        response = send_file(zip_path, as_attachment=True)
        
        # Clean up
        cleanup_files(template_path, names_path, zip_path)
        for file_path in generated_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return response

    except Exception as e:
        app.logger.error(f"Error processing files: {e}")
        # Clean up any files that might have been created
        cleanup_files(template_path, names_path, None)
        return jsonify({'error': str(e)}), 500

@app.route('/convert-to-pdf', methods=['POST'])
def convert_to_pdf():
    if 'docx_files' not in request.files:
        return jsonify({'error': 'No Word documents provided'}), 400
    
    docx_files = request.files.getlist('docx_files')
    
    try:
        # Validate file types first
        for docx_file in docx_files:
            if docx_file.filename and not allowed_word_file(docx_file.filename):
                return jsonify({
                    'error': f'Invalid file type: {docx_file.filename}. Only Word documents (.doc, .docx) are allowed.'
                }), 400

        # Create temporary directories
        temp_docx_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_docx')
        temp_pdf_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'temp_pdf')
        os.makedirs(temp_docx_dir, exist_ok=True)
        os.makedirs(temp_pdf_dir, exist_ok=True)
        
        # Save uploaded Word files
        saved_paths = []
        for docx_file in docx_files:
            if docx_file.filename:
                path = os.path.join(temp_docx_dir, secure_filename(docx_file.filename))
                docx_file.save(path)
                saved_paths.append(path)
                app.logger.info(f"Saved Word file: {path}")
        
        if not saved_paths:
            return jsonify({'error': 'No valid files uploaded'}), 400
        
        app.logger.info(f"Converting {len(saved_paths)} Word files to PDF")
        
        # Convert to PDFs
        generator = DiplomaGenerator()
        pdf_files = generator.batch_convert_to_pdf(temp_docx_dir, temp_pdf_dir)
        
        app.logger.info(f"Successfully converted {len(pdf_files)} files to PDF")
        
        # Create zip with PDFs
        zip_path = os.path.join(app.config['OUTPUT_FOLDER'], 'converted_pdfs.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf_file in pdf_files:
                zipf.write(pdf_file, pdf_file.name)
                app.logger.info(f"Added {pdf_file.name} to zip file")
        
        @after_this_request
        def cleanup(response):
            try:
                # Cleanup
                if os.path.exists(temp_docx_dir):
                    shutil.rmtree(temp_docx_dir)
                if os.path.exists(temp_pdf_dir):
                    shutil.rmtree(temp_pdf_dir)
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                app.logger.info("Cleanup completed successfully")
            except Exception as e:
                app.logger.error(f"Cleanup error: {e}")
            return response
        
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name='converted_pdfs.zip'
        )
        
    except Exception as e:
        app.logger.error(f"Error converting to PDF: {e}")
        # Cleanup on error
        if os.path.exists(temp_docx_dir):
            shutil.rmtree(temp_docx_dir)
        if os.path.exists(temp_pdf_dir):
            shutil.rmtree(temp_pdf_dir)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return jsonify({
            'error': str(e),
            'message': 'Failed to convert documents to PDF'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 