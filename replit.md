# Image Resizer API

## Overview

This is a Flask-based web application that provides an image resizing API service. The application allows users to upload images or provide image URLs, specify desired dimensions, and receive resized images in various formats. It supports both file uploads and URL-based image processing with high-quality image manipulation using PIL (Pillow).

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python 3.11)
- **Image Processing**: PIL (Pillow) for high-quality image manipulation
- **Web Server**: Gunicorn for production deployment
- **HTTP Client**: Requests library for URL-based image fetching

### Frontend Architecture
- **UI Framework**: Bootstrap 5 with dark theme
- **JavaScript**: Vanilla JS for form handling and API interactions
- **Icons**: Font Awesome for UI elements
- **Styling**: Custom CSS with dark theme support

### Application Structure
```
├── main.py          # Application entry point
├── app.py           # Main Flask application with API endpoints
├── templates/       # HTML templates
│   └── index.html   # Web interface
├── static/          # Static assets
│   ├── css/style.css
│   └── js/app.js
└── pyproject.toml   # Dependencies and project config
```

## Key Components

### Image Processing Engine
- **Input Validation**: Supports JPEG, PNG, WebP, and GIF formats
- **Output Formats**: JPEG, PNG, and WebP with quality optimization
- **Dimension Validation**: Maximum 5000px width/height, 50MB file size limit
- **Quality Control**: Automatic format selection and quality preservation

### API Endpoints
- **Web Interface**: `/` - Serves the main web application
- **Image Processing**: `/resize` - Handles image resizing requests
- **Input Methods**: Support for both file uploads and URL-based processing

### Security Features
- File size limits (50MB maximum)
- Dimension restrictions (5000px maximum)
- Secure filename handling
- Input format validation
- MIME type verification

## Data Flow

1. **Input Processing**: User uploads file or provides URL through web interface
2. **Validation**: System validates file format, size, and dimensions
3. **Image Processing**: PIL processes the image with specified dimensions
4. **Output Generation**: Resized image is returned in requested format
5. **Response**: Client receives processed image or error message

### Processing Pipeline
```
Image Input → Format Validation → Dimension Validation → 
PIL Processing → Quality Optimization → Output Format → Response
```

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and routing
- **Pillow**: Image processing and manipulation
- **Requests**: HTTP client for URL-based image fetching
- **Werkzeug**: WSGI utilities and security helpers
- **Gunicorn**: Production WSGI server

### System Dependencies
- **PostgreSQL**: Database system (configured but not actively used)
- **Image Libraries**: freetype, libjpeg, libwebp, openjpeg, libtiff
- **SSL/TLS**: OpenSSL for secure connections

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library
- **Modern Browsers**: JavaScript ES6+ support required

## Deployment Strategy

### Production Configuration
- **Server**: Gunicorn with auto-scaling deployment target
- **Binding**: 0.0.0.0:5000 with port reuse and reload capabilities
- **Environment**: Replit with Nix package management
- **Session Management**: Flask sessions with configurable secret key

### Development Setup
- **Hot Reload**: Automatic reloading during development
- **Debug Mode**: Comprehensive logging and error reporting
- **Port Configuration**: Flexible port binding for development

### Scalability Considerations
- Stateless design for horizontal scaling
- Memory-efficient image processing
- Configurable resource limits
- Ready for load balancer integration

## Changelog

- June 20, 2025: Enhanced interface to clearly show JPG format support alongside JPEG
- June 17, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.