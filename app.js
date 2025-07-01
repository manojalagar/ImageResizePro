document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const progressSection = document.getElementById('progressSection');
    const errorSection = document.getElementById('errorSection');
    const successSection = document.getElementById('successSection');
    const errorMessage = document.getElementById('errorMessage');
    const downloadLink = document.getElementById('downloadLink');
    const submitBtn = document.getElementById('submitBtn');
    const fileInput = document.getElementById('file');
    const urlInput = document.getElementById('url');

    // Clear URL when file is selected
    fileInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            urlInput.value = '';
        }
    });

    // Clear file when URL is entered
    urlInput.addEventListener('input', function() {
        if (this.value.trim()) {
            fileInput.value = '';
        }
    });

    // Form submission
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Hide previous results
        hideAllAlerts();
        
        // Validate inputs
        const file = fileInput.files[0];
        const url = urlInput.value.trim();
        const width = document.getElementById('width').value;
        const height = document.getElementById('height').value;
        
        if (!file && !url) {
            showError('Please select a file or enter an image URL.');
            return;
        }
        
        if (!width || !height) {
            showError('Please enter both width and height.');
            return;
        }
        
        if (parseInt(width) <= 0 || parseInt(height) <= 0) {
            showError('Width and height must be positive numbers.');
            return;
        }
        
        if (parseInt(width) > 5000 || parseInt(height) > 5000) {
            showError('Width and height must not exceed 5000 pixels.');
            return;
        }
        
        // Show progress
        showProgress();
        disableForm(true);
        
        try {
            // Prepare form data
            const formData = new FormData();
            
            if (file) {
                formData.append('file', file);
            }
            
            if (url) {
                formData.append('url', url);
            }
            
            formData.append('width', width);
            formData.append('height', height);
            
            const format = document.getElementById('format').value;
            if (format) {
                formData.append('format', format);
            }
            
            const preserveAspectRatio = document.getElementById('preserve_aspect_ratio').checked;
            if (preserveAspectRatio) {
                formData.append('preserve_aspect_ratio', 'true');
            }
            
            // Make API request
            const response = await fetch('/api/resize', {
                method: 'POST',
                body: formData
            });
            
            hideProgress();
            
            if (response.ok) {
                // Success - create download link
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const filename = getFilenameFromResponse(response) || 'resized_image';
                
                downloadLink.href = downloadUrl;
                downloadLink.download = filename;
                downloadLink.textContent = `Download ${filename}`;
                
                showSuccess();
                
                // Auto-download
                downloadLink.click();
            } else {
                // Error response
                const errorData = await response.json();
                showError(errorData.error || 'An error occurred while processing the image.');
            }
            
        } catch (error) {
            hideProgress();
            showError('Network error: ' + error.message);
        } finally {
            disableForm(false);
        }
    });
    
    function showProgress() {
        progressSection.style.display = 'block';
    }
    
    function hideProgress() {
        progressSection.style.display = 'none';
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorSection.style.display = 'block';
    }
    
    function showSuccess() {
        successSection.style.display = 'block';
    }
    
    function hideAllAlerts() {
        progressSection.style.display = 'none';
        errorSection.style.display = 'none';
        successSection.style.display = 'none';
    }
    
    function disableForm(disabled) {
        const formElements = uploadForm.querySelectorAll('input, select, button');
        formElements.forEach(element => {
            element.disabled = disabled;
        });
        
        if (disabled) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        } else {
            submitBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Resize Image';
        }
    }
    
    function getFilenameFromResponse(response) {
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const matches = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (matches && matches[1]) {
                return matches[1].replace(/['"]/g, '');
            }
        }
        return null;
    }
    
    // Add some example dimensions for common use cases
    const commonSizes = [
        { name: 'Instagram Square', width: 1080, height: 1080 },
        { name: 'Instagram Portrait', width: 1080, height: 1350 },
        { name: 'Facebook Cover', width: 1200, height: 630 },
        { name: 'Twitter Header', width: 1500, height: 500 },
        { name: 'HD (1080p)', width: 1920, height: 1080 },
        { name: 'Thumbnail', width: 300, height: 300 }
    ];
    
    // Add quick size buttons
    const quickSizeContainer = document.createElement('div');
    quickSizeContainer.className = 'mb-3';
    quickSizeContainer.innerHTML = '<label class="form-label">Quick Sizes:</label><div id="quickSizeButtons" class="d-flex flex-wrap gap-2"></div>';
    
    const widthInput = document.getElementById('width');
    widthInput.parentNode.parentNode.parentNode.insertBefore(quickSizeContainer, widthInput.parentNode.parentNode);
    
    const quickSizeButtons = document.getElementById('quickSizeButtons');
    
    commonSizes.forEach(size => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-outline-secondary btn-sm';
        btn.textContent = size.name;
        btn.addEventListener('click', function() {
            document.getElementById('width').value = size.width;
            document.getElementById('height').value = size.height;
        });
        quickSizeButtons.appendChild(btn);
    });
});
