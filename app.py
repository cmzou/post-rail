import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

BASE_DIR = os.path.abspath("files")

app = Flask(__name__)
os.makedirs(BASE_DIR, exist_ok=True)


@app.route("/")
def index():
    files = os.listdir(BASE_DIR)
    return render_template("index.html", files=files)


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    if f:
        f.save(os.path.join(BASE_DIR, f.filename))
    return redirect(url_for("index"))


@app.route("/delete/<filename>")
def delete(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for("index"))


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(BASE_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
