#!/usr/bin/env python3
"""
Pixel Art Converter - Main Entry Point

Run this file to start the Flask development server.
"""

import os
from app import create_app
from app.config import config_by_name

# Get configuration from environment or use development
config_name = os.environ.get('FLASK_ENV', 'development')
config_class = config_by_name.get(config_name, config_by_name['default'])

app = create_app(config_class)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = config_name == 'development'
    
    print(f"Starting Pixel Art Converter on port {port}")
    print(f"Environment: {config_name}")
    print(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
