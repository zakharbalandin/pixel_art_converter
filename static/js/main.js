/**
 * Pixel Art Converter - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Pixel Art Converter loaded');
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function(flash) {
        setTimeout(function() {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s';
            setTimeout(function() {
                flash.remove();
            }, 500);
        }, 5000);
    });
});

/**
 * API helper functions for programmatic access
 */
const PixelArtAPI = {
    /**
     * Convert an image file to pixel art
     * @param {File} file - The image file to convert
     * @param {Object} options - Conversion options
     * @returns {Promise} - Promise resolving to conversion result
     */
    convert: async function(file, options = {}) {
        const formData = new FormData();
        formData.append('image', file);
        formData.append('pixel_size', options.pixelSize || 10);
        formData.append('color_count', options.colorCount || 16);
        
        const response = await fetch('/api/convert', {
            method: 'POST',
            body: formData
        });
        
        return response.json();
    },
    
    /**
     * Get conversion statistics
     * @returns {Promise} - Promise resolving to stats object
     */
    getStats: async function() {
        const response = await fetch('/api/stats');
        return response.json();
    }
};

// Export for use in other scripts
window.PixelArtAPI = PixelArtAPI;
