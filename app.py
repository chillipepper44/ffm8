from flask import Flask, request, render_template_string
from ffm_parser import parse_manifest_to_ffm8
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        file = request.files["pdf_file"]
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            try:
                output = parse_manifest_to_ffm8(file_path)
            except Exception as e:
                output = f"❌ Error: {str(e)}"
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF to FFM/8 Converter</title>
        <style>
            body { font-family: sans-serif; padding: 20px; background-color: #f4f4f4; }
            h1 { color: #333; }
            textarea { width: 100%; height: 400px; margin-top: 20px; font-family: monospace; white-space: pre; }
            input[type="submit"] { margin-top: 10px; padding: 10px 20px; }
        </style>
    </head>
    <body>
        <h1>Convert PDF Manifest to FFM/8 Format</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="pdf_file" accept=".pdf" required>
            <br>
            <input type="submit" value="Convert">
        </form>
        <textarea readonly>{{ output }}</textarea>
    </body>
    </html>
    """, output=output)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

