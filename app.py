import os
import yaml
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, jsonify
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

import datetime
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - %(levelname)s - %(name)s: %(message)s",
)

IMAGE_DIR = "images"
SECRETS_FILE = "./secrets.yml"
STATIC_DIR = "./static"
BASE_DIR = os.path.abspath(os.path.join(STATIC_DIR, IMAGE_DIR))
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE = 1024 * 1024  * MAX_FILE_SIZE_MB

special_day_to_texts = {
    "2026-04-09": "CSS Rainbow Text"
}

class Secrets:
    def __init__(self) -> None:
        self.config = yaml.safe_load(open(SECRETS_FILE))

secrets = Secrets()

app = Flask(__name__, static_folder=STATIC_DIR)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
app.secret_key = secrets.config["secret_key"]

app.wsgi_app = ProxyFix(
    app.wsgi_app,x_for=1, x_proto=1, x_host=1, x_prefix=1
)

def is_allowed_file_ext(filename):
    file_ext = os.path.splitext(filename)[1]
    return "." in filename and file_ext in ALLOWED_EXTENSIONS

def safe_path(filename):
    # Prevent path traversal
    filename = secure_filename(filename)
    full_path = os.path.abspath(os.path.join(BASE_DIR, filename))
    if not full_path.startswith(BASE_DIR):
        abort(403)
    return full_path

@app.route("/")
def index():
    files = os.listdir(BASE_DIR)
    files = [f for f in files if os.path.splitext(f)[1] in ALLOWED_EXTENSIONS]

    today =  datetime.datetime.today().strftime("%Y-%m-%d")

    if today in special_day_to_texts:
        marquee_text = special_day_to_texts[today]
    else:
        marquee_text = ""
    return render_template("index.html", files=files, IMAGE_DIR=BASE_DIR, marquee_text=marquee_text)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        abort(400)

    f = request.files["file"]

    if f.filename == "":
        abort(400)

    if not is_allowed_file_ext(f.filename):
        abort(400)

    filename = secure_filename(f.filename)
    path = safe_path(filename)

    # Prevent overwrite (optional)
    if os.path.exists(path):
        abort(409)

    f.save(path)
    return redirect(url_for("index"))

@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    path = safe_path(filename)

    if os.path.exists(path):
        os.remove(path)
        logger.info(f"File removed: {path}")

    return redirect(url_for("index"))

@app.route("/download/<filename>")
def download(filename):
    filename = secure_filename(filename)
    return send_from_directory(BASE_DIR, filename, as_attachment=True)

@app.route("/images/<filename>")
def serve_image(filename):
    filename = secure_filename(filename)
    return send_from_directory(BASE_DIR, filename)

@app.route("/restart", methods=["POST"])
def restart_service():
    logger.info(f"Application restarted")
    return jsonify({"message": "Button pressed"}), 200

@app.errorhandler(413)
def too_large(e):
    return f"File too large (max {MAX_FILE_SIZE_MB} MB)", 413


if __name__ == "__main__":
    app.run(debug=True)
