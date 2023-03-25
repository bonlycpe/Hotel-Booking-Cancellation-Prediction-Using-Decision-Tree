import os

import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
from dst_script import dst_process,input_validation

ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    invalid = False
    table = pd.read_csv("example/variable.csv", encoding = "ISO-8859-1")
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            new_filename = f'{filename.split(".")[0]}.csv'
            save_location = os.path.join('input', new_filename)
            file.save(save_location)

            if not input_validation(save_location):
                invalid = True
            else:
                df = dst_process(save_location)
                return render_template('download.html', files=os.listdir('output'), table = df.to_html())
        else:
            invalid = True

    elif request.method == 'GET':
        invalid = False
    
    return render_template('upload.html', invalid=invalid , files=os.listdir('example') , table = table.to_html())

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('output', filename)

@app.route('/download_example/<filename>')
def download_example_file(filename):
    return send_from_directory('example', filename)


if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)