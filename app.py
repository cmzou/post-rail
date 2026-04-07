import os
import yaml
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

IMAGE_DIR = "./static/images"
SECRETS_FILE = "./secrets.yml"
BASE_DIR = os.path.abspath(IMAGE_DIR)
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE = 1024 * 1024  * MAX_FILE_SIZE_MB

class Secrets:
    def __init__(self) -> None:
        self.config = yaml.safe_load(open(SECRETS_FILE))

secrets = Secrets()

app = Flask(__name__)
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
    return render_template("index.html", files=files, IMAGE_DIR=IMAGE_DIR)

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
        # os.remove(path)
        print(f"file {path} has been removed")

    return redirect(url_for("index"))

@app.route("/download/<filename>")
def download(filename):
    filename = secure_filename(filename)
    return send_from_directory(BASE_DIR, filename, as_attachment=True)

@app.errorhandler(413)
def too_large(e):
    return f"File too large (max {MAX_FILE_SIZE_MB} MB)", 413


if __name__ == "__main__":
    app.run(debug=True)
