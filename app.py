import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath("files")
ALLOWED_EXTENSIONS = {"txt", "png", "jpg", "jpeg", "gif", "pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
app.secret_key = "change-this-secret-key"

os.makedirs(BASE_DIR, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
    return render_template("index.html", files=files)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        abort(400)

    f = request.files["file"]

    if f.filename == "":
        abort(400)

    if not allowed_file(f.filename):
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

    return redirect(url_for("index"))


@app.route("/download/<filename>")
def download(filename):
    filename = secure_filename(filename)
    return send_from_directory(BASE_DIR, filename, as_attachment=True)


@app.errorhandler(413)
def too_large(e):
    return "File too large (max 5MB)", 413


if __name__ == "__main__":
    app.run(debug=True)
