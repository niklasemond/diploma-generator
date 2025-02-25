from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from diploma_generator import DiplomaGenerator

app = Flask(__name__)

# Use environment variables for configuration
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.environ.get('OUTPUT_FOLDER', 'output')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png'}

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

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

    if template_file.filename == '':
        return jsonify({'error': 'No template selected'}), 400
    
    if names_file.filename == '':
        return jsonify({'error': 'No names file selected'}), 400

    if not allowed_file(template_file.filename):
        return jsonify({'error': 'Invalid template file format'}), 400

    try:
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
        generator.generate_diplomas(names, output_dir, placeholder)

        # Create zip file of all generated diplomas
        zip_path = os.path.join(output_dir, 'diplomas.zip')
        os.system(f'zip -j {zip_path} {output_dir}/*.pdf')  # Adjust based on output format

        response = send_file(zip_path, as_attachment=True)
        
        # Clean up after sending the file
        cleanup_files(template_path, names_path, zip_path)
        
        return response

    except Exception as e:
        app.logger.error(f"Error processing files: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 