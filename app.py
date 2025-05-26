# app.py
from flask import Flask, render_template, request, redirect, url_for
import os
from ffm_parser import parse_manifest_to_ffm8

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("manifest")
    if not file or not file.filename.endswith(".pdf"):
        return "Invalid file. Please upload a PDF.", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    ffm_output = parse_manifest_to_ffm8(filepath)
    return render_template("index.html", output=ffm_output)

if __name__ == "__main__":
    app.run(debug=True)
