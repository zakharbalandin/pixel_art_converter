"""Flask Web Application for Pixel Art Converter"""

import io
import os
import time
import uuid
from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from converter import PixelArtConverter
from models import Conversion, User, db, get_database_url

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024


def create_app(config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["RESULT_FOLDER"] = RESULT_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    if config:
        app.config.update(config)
    db.init_app(app)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RESULT_FOLDER"], exist_ok=True)
    with app.app_context():
        db.create_all()
    register_routes(app)
    return app


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    if "user_id" in session:
        return User.query.get(session["user_id"])
    return None


def register_routes(app):
    @app.context_processor
    def inject_user():
        return dict(current_user=get_current_user())

    @app.route("/")
    def index():
        palettes = PixelArtConverter.get_available_palettes()
        return render_template("index.html", palettes=palettes)

    @app.route("/convert", methods=["POST"])
    def convert():
        start_time = time.time()
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        pixel_size = request.form.get("pixel_size", 8, type=int)
        palette = request.form.get("palette", "retro")
        pixel_size = max(1, min(64, pixel_size))
        if palette not in PixelArtConverter.get_available_palettes():
            palette = "retro"
        try:
            image_data = file.read()
            original_image = Image.open(io.BytesIO(image_data))
            original_width, original_height = original_image.size
            converter = PixelArtConverter(pixel_size=pixel_size, palette=palette)
            result_image = converter.convert(original_image)
            result_buffer = io.BytesIO()
            result_image.save(result_buffer, format="PNG")
            result_buffer.seek(0)
            result_data = result_buffer.getvalue()
            processing_time = int((time.time() - start_time) * 1000)
            file_uuid = str(uuid.uuid4())[:8]
            original_filename = secure_filename(file.filename)
            result_filename = f"pixel_art_{file_uuid}.png"
            original_path = os.path.join(
                app.config["UPLOAD_FOLDER"], f"{file_uuid}_{original_filename}"
            )
            result_path = os.path.join(app.config["RESULT_FOLDER"], result_filename)
            with open(original_path, "wb") as f:
                f.write(image_data)
            with open(result_path, "wb") as f:
                f.write(result_data)
            conversion = Conversion(
                user_id=session.get("user_id"),
                original_filename=original_filename,
                original_size=len(image_data),
                original_width=original_width,
                original_height=original_height,
                pixel_size=pixel_size,
                palette=palette,
                result_filename=result_filename,
                result_size=len(result_data),
                processing_time_ms=processing_time,
                status="completed",
            )
            db.session.add(conversion)
            db.session.commit()
            return jsonify(
                {
                    "success": True,
                    "conversion_id": conversion.id,
                    "result_filename": result_filename,
                    "processing_time_ms": processing_time,
                    "original_size": len(image_data),
                    "result_size": len(result_data),
                }
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/result/<filename>")
    def get_result(filename):
        filename = secure_filename(filename)
        filepath = os.path.join(app.config["RESULT_FOLDER"], filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        return send_file(filepath, mimetype="image/png")

    @app.route("/download/<filename>")
    def download_result(filename):
        filename = secure_filename(filename)
        filepath = os.path.join(app.config["RESULT_FOLDER"], filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        return send_file(filepath, as_attachment=True, download_name=filename)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            if not username or not email or not password:
                flash("All fields are required.", "error")
                return render_template("register.html")
            if len(password) < 6:
                flash("Password must be at least 6 characters.", "error")
                return render_template("register.html")
            if User.query.filter_by(username=username).first():
                flash("Username already exists.", "error")
                return render_template("register.html")
            if User.query.filter_by(email=email).first():
                flash("Email already registered.", "error")
                return render_template("register.html")
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session["user_id"] = user.id
                flash(f"Welcome back, {user.username}!", "success")
                return redirect(url_for("index"))
            else:
                flash("Invalid username or password.", "error")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop("user_id", None)
        flash("You have been logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/history")
    @login_required
    def history():
        user = get_current_user()
        conversions = (
            Conversion.query.filter_by(user_id=user.id)
            .order_by(Conversion.created_at.desc())
            .limit(50)
            .all()
        )
        return render_template("history.html", conversions=conversions)

    @app.route("/api/palettes")
    def api_palettes():
        return jsonify({"palettes": PixelArtConverter.get_available_palettes()})

    @app.route("/api/stats")
    def api_stats():
        from datetime import datetime

        total_conversions = Conversion.query.count()
        today = datetime.utcnow().date()
        today_conversions = Conversion.query.filter(
            db.func.date(Conversion.created_at) == today
        ).count()
        return jsonify(
            {
                "total_conversions": total_conversions,
                "today_conversions": today_conversions,
            }
        )

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", error="Page not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", error="Internal server error"), 500

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"error": "File too large. Maximum size is 16MB."}), 413


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
