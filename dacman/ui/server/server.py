# server.py
import os
from flask import Flask, flash, request, redirect
from flask import render_template, json, send_from_directory
from werkzeug.utils import secure_filename
from astropy.io import fits
import pandas as pd

from dacman import Executor, DataDiffer
import dacman
from dacman.plugins.default import DefaultPlugin
from flagging import read_csv


app = Flask(__name__, static_folder='../fits/build/static', template_folder='../fits/build')

UPLOAD_FOLDER = os.environ.get('DEDUCE_UPLOAD_FOLDER', '/Users/absho/workspace/lbnl/deduce/boris/ui/flask_uploads')
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/base/<path:filename>')
def base_static(filename):
    return send_from_directory(app.root_path + '/', filename)

@app.route('/api/fitsinfo')
def api_fits_info():
    hdul = fits.open('../spCFrame-b1-00161868.fits')
    output = hdul.info(output=False)
    return json.jsonify(output)

@app.route('/api/dacmantest')
def api_dacman_test():
    file1 = '../../../examples/data/simple/v0/file1'
    file2 = '../../../examples/data/simple/v1/file1'
    comparisons = [(file1, file2)]
    differ = DataDiffer(comparisons, executor=Executor.DEFAULT)
    differ.use_plugin(DefaultPlugin)
    results = differ.start()
    print(results)
    return json.jsonify(results)


@app.route('/api/fitschangesummary')
def api_fits_change_summary():
    json_data = open('./output/summary.json')
    data = json.load(json_data)
    return json.jsonify(data)


@app.route('/api/fits/plugin', methods = ['POST', 'GET'])
def run_fits_change_analysis():
    from pathlib import Path

    path_base = Path.home() / '/Users/sarahpoon/Documents/LBL/deduce/prototype/p6/dac-man/dacman/ui/exampledata/sdss_sample'

    # TODO this should be read from the request instead
    req_data = {
        'path': {
            'A': path_base / 'v5_6_5/6838/spCFrame-b1-00161868.fits',
            'B': path_base / 'v5_7_0/6838/spCFrame-b1-00161868.fits',
        },
        'metrics': [
            {
                'name': 'array_difference',
                'params': {
                    'extension': 1,
                }
            },
        ]
    }

    from dacman.plugins.fits import FITSUIPlugin

    comparator = FITSUIPlugin(metrics=req_data['metrics'])
    res = comparator.compare(req_data['path']['A'], req_data['path']['B'])

    res['outputs'] = []

    for output in ['a.png', 'b.png', 'delta.png']:
        path = Path(output)
        output_data = {
            'path_absolute': str(path.absolute),
            'filename': path.name,
            'filetype': path.suffix.replace('.', '', 1),
        }

    return json.jsonify(res)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# For Flagging
@app.route('/flagging/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'upload_dataset' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['upload_dataset']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        data = read_csv(file_path)
        return json.jsonify(data)


@app.route('/hello')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
