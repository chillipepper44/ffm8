from flask import Flask, render_template, request
import tempfile
from ffm_parser import parse_manifest_to_ffm8_precise

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith(".pdf"):
            # บันทึกไฟล์ชั่วคราว
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                file.save(tmp.name)
                pdf_path = tmp.name

            try:
                output = parse_manifest_to_ffm8_precise(pdf_path)
            except Exception as e:
                output = f"เกิดข้อผิดพลาด: {str(e)}"

    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)
