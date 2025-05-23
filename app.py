from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from diploma_generator import DiplomaGenerator
import zipfile
import time

app = Flask(__name__)

# Use environment variables for configuration
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.environ.get('OUTPUT_FOLDER', 'output')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() == '.pdf'

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
        return jsonify({'error': 'Only PDF templates are supported'}), 400

    template_path = None
    names_path = None
    zip_path = None
    generated_files = []

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
        generated_files = generator.generate_diplomas(
            names, 
            output_dir, 
            placeholder
        )

        # Verify all files exist and are readable
        for file_path in generated_files:
            if not os.path.exists(file_path):
                raise ValueError(f"Generated file {file_path} does not exist")
            try:
                # Try to open and read the file to verify it's valid
                with open(file_path, 'rb') as f:
                    content = f.read(1024)
                    if not content:
                        raise ValueError(f"Generated file {file_path} is empty")
                    # Verify it's a PDF
                    if not content.startswith(b'%PDF-'):
                        raise ValueError(f"Generated file {file_path} is not a valid PDF")
            except Exception as e:
                raise ValueError(f"Generated file {file_path} is not readable: {str(e)}")

        # Create zip file with a temporary name first
        temp_zip_path = os.path.join(output_dir, f'diplomas_{int(time.time())}.zip')
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in generated_files:
                # Add each file with its basename
                zipf.write(file_path, os.path.basename(file_path))
                # Verify the file was added to the zip
                if os.path.basename(file_path) not in zipf.namelist():
                    raise ValueError(f"Failed to add {file_path} to zip file")

        # Verify the zip file
        if not os.path.exists(temp_zip_path):
            raise ValueError("Failed to create zip file")
        
        # Try to read the zip file to verify it's valid
        with zipfile.ZipFile(temp_zip_path, 'r') as zipf:
            if not zipf.namelist():
                raise ValueError("Zip file is empty")
            # Verify each file in the zip
            for name in zipf.namelist():
                try:
                    content = zipf.read(name)
                    # Verify it's a PDF
                    if not content.startswith(b'%PDF-'):
                        raise ValueError(f"File {name} in zip is not a valid PDF")
                except Exception as e:
                    raise ValueError(f"Invalid file in zip: {name}")

        # Move the temporary zip to the final location
        zip_path = os.path.join(output_dir, 'diplomas.zip')
        if os.path.exists(zip_path):
            os.remove(zip_path)
        os.rename(temp_zip_path, zip_path)

        response = send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name='diplomas.zip'
        )

        # Clean up files after sending
        @response.call_on_close
        def cleanup():
            try:
                if template_path and os.path.exists(template_path):
                    os.remove(template_path)
                if names_path and os.path.exists(names_path):
                    os.remove(names_path)
                if zip_path and os.path.exists(zip_path):
                    os.remove(zip_path)
                for file_path in generated_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception as e:
                app.logger.error(f"Error during cleanup: {str(e)}")

        return response

    except Exception as e:
        # Clean up any files that might have been created
        try:
            if template_path and os.path.exists(template_path):
                os.remove(template_path)
            if names_path and os.path.exists(names_path):
                os.remove(names_path)
            if zip_path and os.path.exists(zip_path):
                os.remove(zip_path)
            for file_path in generated_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
        except:
            pass
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 