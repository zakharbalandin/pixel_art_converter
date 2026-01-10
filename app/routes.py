"""
Flask Application

Main Flask application for the Pixel Art Converter web interface.
"""

import os
import time
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
from werkzeug.utils import secure_filename
from functools import wraps

from app.models import db, User, Conversion, init_db
from app.converter import PixelArtConverter
from app.config import Config


def create_app(config_class=Config):
    """Application factory pattern."""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Register routes
    register_routes(app)
    
    return app


def login_required(f):
    """Decorator to require login for certain routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def register_routes(app):
    """Register all application routes."""
    
    @app.route('/')
    def index():
        """Home page with upload form."""
        return render_template('index.html')
    
    @app.route('/convert', methods=['POST'])
    def convert():
        """Handle image conversion."""
        if 'image' not in request.files:
            flash('No image file provided', 'error')
            return redirect(url_for('index'))
        
        file = request.files['image']
        
        if file.filename == '':
            flash('No image selected', 'error')
            return redirect(url_for('index'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload an image.', 'error')
            return redirect(url_for('index'))
        
        # Get conversion parameters
        try:
            pixel_size = int(request.form.get('pixel_size', 10))
            color_count = int(request.form.get('color_count', 16))
        except ValueError:
            flash('Invalid conversion parameters', 'error')
            return redirect(url_for('index'))
        
        # Validate parameters
        pixel_size = max(1, min(50, pixel_size))
        color_count = max(2, min(256, color_count))
        
        # Generate unique filenames
        unique_id = str(uuid.uuid4())[:8]
        original_filename = secure_filename(file.filename)
        base_name = os.path.splitext(original_filename)[0]
        extension = os.path.splitext(original_filename)[1]
        
        input_filename = f"{unique_id}_{original_filename}"
        output_filename = f"{unique_id}_{base_name}_pixel{extension}"
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Save uploaded file
        file.save(input_path)
        
        # Convert image
        try:
            start_time = time.time()
            converter = PixelArtConverter(pixel_size=pixel_size, color_count=color_count)
            result = converter.convert(input_path, output_path)
            processing_time = (time.time() - start_time) * 1000
            
            # Save conversion record to database
            conversion = Conversion(
                user_id=session.get('user_id'),
                original_filename=original_filename,
                output_filename=output_filename,
                original_width=result['original_size'][0],
                original_height=result['original_size'][1],
                output_width=result['output_size'][0],
                output_height=result['output_size'][1],
                pixel_size=pixel_size,
                color_count=color_count,
                processing_time_ms=processing_time
            )
            db.session.add(conversion)
            db.session.commit()
            
            flash('Image converted successfully!', 'success')
            return render_template('result.html', 
                                   original=input_filename,
                                   output=output_filename,
                                   stats=result,
                                   processing_time=f"{processing_time:.2f}")
            
        except Exception as e:
            flash(f'Conversion failed: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        """Serve uploaded files."""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/outputs/<filename>')
    def output_file(filename):
        """Serve converted files."""
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration."""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            if not username or not email or not password:
                flash('All fields are required', 'error')
                return render_template('register.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters', 'error')
                return render_template('register.html')
            
            # Check if user exists
            if User.query.filter_by(username=username).first():
                flash('Username already taken', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('register.html')
            
            # Create new user
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login."""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['username'] = user.username
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """User logout."""
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/history')
    @login_required
    def history():
        """View conversion history."""
        conversions = Conversion.query.filter_by(user_id=session['user_id'])\
                                      .order_by(Conversion.created_at.desc())\
                                      .limit(50).all()
        return render_template('history.html', conversions=conversions)
    
    @app.route('/api/convert', methods=['POST'])
    def api_convert():
        """API endpoint for image conversion."""
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        try:
            pixel_size = int(request.form.get('pixel_size', 10))
            color_count = int(request.form.get('color_count', 16))
        except ValueError:
            return jsonify({'error': 'Invalid parameters'}), 400
        
        # Generate filenames
        unique_id = str(uuid.uuid4())[:8]
        original_filename = secure_filename(file.filename)
        base_name = os.path.splitext(original_filename)[0]
        extension = os.path.splitext(original_filename)[1]
        
        input_filename = f"{unique_id}_{original_filename}"
        output_filename = f"{unique_id}_{base_name}_pixel{extension}"
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        file.save(input_path)
        
        try:
            start_time = time.time()
            converter = PixelArtConverter(pixel_size=pixel_size, color_count=color_count)
            result = converter.convert(input_path, output_path)
            processing_time = (time.time() - start_time) * 1000
            
            return jsonify({
                'success': True,
                'original_url': url_for('uploaded_file', filename=input_filename, _external=True),
                'output_url': url_for('output_file', filename=output_filename, _external=True),
                'stats': result,
                'processing_time_ms': processing_time
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats')
    def api_stats():
        """Get conversion statistics."""
        total_conversions = Conversion.query.count()
        total_users = User.query.count()
        
        return jsonify({
            'total_conversions': total_conversions,
            'total_users': total_users
        })
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', error='Page not found'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', error='Internal server error'), 500
