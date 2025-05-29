from flask import Flask, render_template, request
from ffm_parser import parse_manifest_to_ffm8
import os

app = Flask(__name__)  # << ไม่ต้องกำหนด template_folder เพราะใช้ค่า default = 'templates'

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        file = request.files.get("manifest")
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            try:
                output = parse_manifest_to_ffm8(file_path)
            except Exception as e:
                output = f"❌ Error: {str(e)}"
    return render_template("index.html", output=output)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
