from flask import Flask, request, render_template
from ffm_parser import parse_manifest_to_ffm8
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    if request.method == "POST":
        file = request.files.get("manifest")
        if file:
            output = parse_manifest_to_ffm8(file)
    return render_template("index.html", output=output)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

