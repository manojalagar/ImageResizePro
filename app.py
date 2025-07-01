import os
import io
import logging
from flask import Flask, request, jsonify, send_file, render_template, flash, redirect, url_for
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename
import requests
from urllib.parse import urlparse
import mimetypes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_dev")

# Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_INPUT_FORMATS = {'JPEG', 'PNG', 'WEBP', 'GIF'}
ALLOWED_OUTPUT_FORMATS = {'JPEG', 'PNG', 'WEBP'}
MAX_DIMENSION = 5000  # Maximum width or height

def validate_image_format(image):
    """Validate if the image format is supported."""
    return image.format in ALLOWED_INPUT_FORMATS

def validate_dimensions(width, height):
    """Validate if the requested dimensions are reasonable."""
    if not width or not height:
        return False, "Both width and height must be provided"
    
    try:
        width = int(width)
        height = int(height)
    except (ValueError, TypeError):
        return False, "Width and height must be valid integers"
    
    if width <= 0 or height <= 0:
        return False, "Width and height must be positive integers"
    
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        return False, f"Width and height must not exceed {MAX_DIMENSION} pixels"
    
    return True, (width, height)

def get_output_format(requested_format, original_format):
    """Determine the output format based on request and original format."""
    if requested_format:
        requested_format = requested_format.upper()
        if requested_format in ALLOWED_OUTPUT_FORMATS:
            return requested_format
    
    # Default to original format if supported, otherwise JPEG
    if original_format in ALLOWED_OUTPUT_FORMATS:
        return original_format
    return 'JPEG'

def resize_image(image, width, height, preserve_aspect_ratio=False):
    """Resize image using high-quality resampling."""
    original_width, original_height = image.size
    
    if preserve_aspect_ratio:
        # Calculate aspect ratio preserving dimensions
        aspect_ratio = original_width / original_height
        requested_ratio = width / height
        
        if requested_ratio > aspect_ratio:
            # Requested is wider, fit by height
            width = int(height * aspect_ratio)
        else:
            # Requested is taller, fit by width
            height = int(width / aspect_ratio)
    
    # Use LANCZOS for high-quality downsampling, BICUBIC for upsampling
    if width * height < original_width * original_height:
        resample = Image.Resampling.LANCZOS
    else:
        resample = Image.Resampling.BICUBIC
    
    resized_image = image.resize((width, height), resample)
    return resized_image

def get_content_type(format_name):
    """Get the appropriate content type for the image format."""
    content_types = {
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
        'WEBP': 'image/webp'
    }
    return content_types.get(format_name, 'image/jpeg')

@app.route('/')
def index():
    """Render the main interface."""
    return render_template('index.html')

@app.route('/api/resize', methods=['POST'])
def resize_image_api():
    """API endpoint for resizing images."""
    try:
        # Get parameters
        width = request.form.get('width') or request.args.get('width')
        height = request.form.get('height') or request.args.get('height')
        output_format = request.form.get('format') or request.args.get('format')
        preserve_aspect_ratio = request.form.get('preserve_aspect_ratio', 'false').lower() == 'true'
        image_url = request.form.get('url') or request.args.get('url')
        
        # Validate dimensions
        valid, result = validate_dimensions(width, height)
        if not valid:
            return jsonify({'error': result}), 400
        
        width, height = result
        
        # Get image from file upload or URL
        image = None
        original_filename = None
        
        if image_url:
            # Process image from URL
            try:
                parsed_url = urlparse(image_url)
                if not parsed_url.scheme in ['http', 'https']:
                    return jsonify({'error': 'Invalid URL scheme. Only HTTP and HTTPS are allowed.'}), 400
                
                response = requests.get(image_url, timeout=30, stream=True)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    return jsonify({'error': 'URL does not point to an image'}), 400
                
                # Check file size
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > MAX_FILE_SIZE:
                    return jsonify({'error': f'Image file too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
                
                image_data = io.BytesIO()
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    downloaded_size += len(chunk)
                    if downloaded_size > MAX_FILE_SIZE:
                        return jsonify({'error': f'Image file too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
                    image_data.write(chunk)
                
                image_data.seek(0)
                image = Image.open(image_data)
                original_filename = os.path.basename(parsed_url.path) or 'image'
                
            except requests.RequestException as e:
                return jsonify({'error': f'Failed to download image: {str(e)}'}), 400
            except Exception as e:
                return jsonify({'error': f'Failed to process image from URL: {str(e)}'}), 400
        
        elif 'file' in request.files:
            # Process uploaded file
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
            
            try:
                image = Image.open(file.stream)
                original_filename = secure_filename(file.filename)
            except Exception as e:
                return jsonify({'error': f'Invalid image file: {str(e)}'}), 400
        
        else:
            return jsonify({'error': 'No image provided. Use either file upload or URL parameter.'}), 400
        
        # Validate image format
        if not validate_image_format(image):
            return jsonify({'error': f'Unsupported image format. Supported formats: {", ".join(ALLOWED_INPUT_FORMATS)}'}), 400
        
        # Convert RGBA to RGB for JPEG output
        original_format = image.format
        output_fmt = get_output_format(output_format, original_format)
        
        if output_fmt == 'JPEG' and image.mode in ['RGBA', 'LA']:
            # Create white background for transparency
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
            else:
                background.paste(image)
            image = background
        
        # Resize the image
        resized_image = resize_image(image, width, height, preserve_aspect_ratio)
        
        # Save to BytesIO
        output_buffer = io.BytesIO()
        save_kwargs = {}
        
        if output_fmt == 'JPEG':
            save_kwargs['quality'] = 95
            save_kwargs['optimize'] = True
        elif output_fmt == 'PNG':
            save_kwargs['optimize'] = True
        elif output_fmt == 'WEBP':
            save_kwargs['quality'] = 95
            save_kwargs['method'] = 6  # Best compression
        
        resized_image.save(output_buffer, format=output_fmt, **save_kwargs)
        output_buffer.seek(0)
        
        # Generate filename
        name, ext = os.path.splitext(original_filename)
        if not name:
            name = 'resized_image'
        
        extension_map = {'JPEG': '.jpg', 'PNG': '.png', 'WEBP': '.webp'}
        new_filename = f"{name}_{width}x{height}{extension_map[output_fmt]}"
        
        return send_file(
            output_buffer,
            mimetype=get_content_type(output_fmt),
            as_attachment=True,
            download_name=new_filename
        )
        
    except Exception as e:
        app.logger.error(f"Error processing image: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/info', methods=['GET'])
def api_info():
    """Get API information and supported formats."""
    return jsonify({
        'supported_input_formats': list(ALLOWED_INPUT_FORMATS),
        'supported_output_formats': list(ALLOWED_OUTPUT_FORMATS),
        'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024),
        'max_dimension': MAX_DIMENSION,
        'endpoints': {
            'resize': {
                'method': 'POST',
                'url': '/api/resize',
                'parameters': {
                    'width': 'integer (required)',
                    'height': 'integer (required)',
                    'format': 'string (optional) - output format',
                    'preserve_aspect_ratio': 'boolean (optional) - default false',
                    'file': 'file upload (optional)',
                    'url': 'string (optional) - image URL'
                }
            }
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
