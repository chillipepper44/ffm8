import os
from flask import Flask, request, render_template
from ffm_parser import parse_manifest_to_ffm8

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        file = request.files.get('manifest')
        if file:
            result = parse_manifest_to_ffm8(file)
    return render_template('index.html', output=result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
