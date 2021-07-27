# server.py
import datetime
import os
import uuid
import glob
from pathlib import Path
import tarfile

from flask import Flask, flash, request, redirect
from flask import render_template, json, send_from_directory
from werkzeug.utils import secure_filename

from flagging.flagging import read_csv, sample_data, qa_flagging_app_deploy
from flagging.flagging import save_metadata, combine_csv_files, clean_up
from datadiff import (
    BaseResource,
    Dataset,
    DatasetFile,
    H5Object,
    Comparison,
    ModelOutputComparator,
)


class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseResource):
            return obj.dict()
        if isinstance(obj, os.PathLike):
            return os.fspath(obj)
        return super().default(obj)


app = Flask(__name__, static_folder='../fits/build/static', template_folder='../fits/build')

app.config['JSON_SORT_KEYS'] = False
app.json_encoder = ExtendedEncoder

UPLOAD_FOLDER = os.environ.get('DEDUCE_UPLOAD_FOLDER', '/data/deduce/uploads')
RESULTS_FOLDER = os.environ.get('DEDUCE_RESULTS_FOLDER', '/data/deduce/runs')
 
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER


Dataset.base_dir = Path(UPLOAD_FOLDER) / 'datasets'
Comparison.base_dir = Path(RESULTS_FOLDER) / 'comparisons'


@app.route('/')
def index():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# For Flagging
@app.route('/flagging/id', methods=['GET'])
def generate_project_id():
    project_id = str(uuid.uuid4())
    return json.jsonify({ 'project_id': project_id })

@app.route('/flagging/upload/<project_id>/<file_index>', methods=['POST'])
def upload_file(project_id, file_index):
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

        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], project_id)
        
        if not os.path.exists(upload_path):
            try:
                os.mkdir(upload_path)
            except FileExistsError:
                pass

        file_path = os.path.join(upload_path, filename)
        file.save(file_path)

        # The disparate variable feature will be implemented here
        # To be precise, the metadata of the variables will be saved here.
        # Such metadata will include the files that has the accompanying
        # variable. I guess we can start with having the variables having
        # matching names to be processed in different variables.
        #
        # The metadata needs to be saved to be loaded by later at the data
        # processing phase.

        # An issue started to appear which is having multiple threads
        # read the same metadata file. I fixed it by having each thread save
        # its own file.

        data = read_csv(file_path)
        save_metadata(data.columns, filename, upload_path)

        formatted_data, data_total_shape = sample_data(data)
        return json.jsonify(
            {
                'file_index': file_index,
                'project_id': project_id,
                'data_total_shape': list(data_total_shape),
                'data': formatted_data
            })

@app.route('/flagging/run/<project_id>', methods=['POST'])
def run_flagging(project_id):
    # check if the post request has the file part
    variable_details = request.get_json()

    datasets_dir = os.path.join(
        app.config['UPLOAD_FOLDER'],
        project_id
    )

    # prev TODO - check if all variables exist in all uploaded files
    # Update July 2021: Because of the disparate variables feature, the files could have
    # different variables!

    # Load the metadata to know which variables will be processed on
    # which files.

    # run the R script on the files, and return the folder where the
    # processing happened
    processing_folder = qa_flagging_app_deploy(
        project_id,
        datasets_dir,
        variable_details,
        app.config['RESULTS_FOLDER']
    )

    output_csv_file, output_zip_file = combine_csv_files(processing_folder)

    output_csv_file = Path(output_csv_file)
    output_zip_file = Path(output_zip_file)

    data = read_csv(output_csv_file)
    fornatted_data, data_total_shape = sample_data(data)

    clean_up(os.path.join(app.config['UPLOAD_FOLDER'], project_id))

    return json.jsonify({
        'data_total_shape': list(data_total_shape),
        'csv_filename': output_csv_file.name,
        'zip_filename': output_zip_file.name,
        'data': fornatted_data
    })

@app.route('/flagging/download/<project_id>', methods=['POST'])
def download(project_id):
    #project_id = request.args.get('project_id')
    print(project_id)
    #print(request.get_json())
    folder_path = os.path.join(app.config['RESULTS_FOLDER'], project_id)
    print(glob.glob(os.path.join(folder_path, "*.csv.gz")))
    file_to_download = glob.glob(os.path.join(folder_path, "*.zip"))[0]
    file_to_download = os.path.basename(file_to_download)
    print("file_to_download:", file_to_download)
    return send_from_directory(folder_path, file_to_download)

@app.route('/flagging/clean/<project_id>', methods=['POST'])
def clean(project_id):
    #clean_up(os.path.join(app.config['UPLOAD_FOLDER'], project_id))
    clean_up(os.path.join(app.config['RESULTS_FOLDER'], project_id))
    return "Data that belongs to project '%s' was deleted" % project_id


def untar(src_path: Path, dst_path: Path):
    assert src_path.exists, "The source path should exist"
    # TODO what should we do with dst_path? how should we deal with it if e.g. it already exists?
    try:
        with tarfile.open(src_path, 'r') as tf:
            tf.extractall(path=dst_path)
    except Exception as e:
        app.logger.error(f'Could not untar file {src_path} into destination directory {dst_path}')
        app.logger.exception(e)
    else:
        app.logger.info(f'File {src_path} extracted successfully into {dst_path}')


def write_stream(stream, dst_path: Path, chunksize=16384):
    read_chunk_size = None
    read_total = 0
    with dst_path.open('bw') as f:
        while read_chunk_size != 0:
            read_chunk = stream.read(chunksize)
            read_chunk_size = len(read_chunk)
            f.write(read_chunk)
            read_total += read_chunk_size
        return read_total


@app.route('/datadiff/contents/datasets', methods=['POST'])
@app.route('/datadiff/upload', methods=['POST'])
def process_upload():
    tmp_path = Path('/tmp/uploaded_file')

    app.logger.info("request:")
    app.logger.info(request.headers)

    key = request.headers.get('X-File-Name', None)
    dataset = Dataset.create(key=key)
    final_dir = dataset.path

    try:
        app.logger.info(f'Starting to save uploaded stream to {tmp_path}')
        write_stream(request.stream, tmp_path)
        app.logger.info(f'size={tmp_path.stat().st_size}')
        app.logger.info(f'Trying to untar the uploaded file into {final_dir}')
        untar(tmp_path, final_dir)
        app.logger.info(f'Removing temporary file')
        tmp_path.unlink()
    except Exception as e:
        app.logger.error('Operation failed')
        app.logger.exception(e)
    else:
        app.logger.info(f'Operation complete. Dataset: {dataset.resource_key}')
        return json.jsonify(dataset)


@app.route('/datadiff/contents/datasets')
def get_datasets():
    datasets = list(Dataset.all())

    return json.jsonify(datasets)


@app.route('/datadiff/contents/datasets/<key>')
def get_dataset(key):
    dataset = Dataset.get(key)
    return json.jsonify(dataset)


@app.route('/datadiff/contents/datasets/<key>/files')
def get_dataset_files(key, limit=50):
    dataset = Dataset.get(key)
    files = list(DatasetFile.all(dataset))[:limit]
    return json.jsonify(files)


@app.route('/datadiff/contents/datasets/<dataset_key>/files/<file_key>/h5')
def get_dataset_file_h5_objects(dataset_key, file_key):
    dataset = Dataset.get(dataset_key)
    file = DatasetFile.get(resource_key=file_key, dataset=dataset)
    h5_content = list(H5Object.all(file=file))
    return json.jsonify(h5_content)


@app.route('/datadiff/contents/datasets/<dataset_key>/files/<file_key>/h5/<h5_key>')
def get_dataset_file_h5_object(dataset_key, file_key, h5_key):
    dataset = Dataset.get(dataset_key)
    file = DatasetFile.get(resource_key=file_key, dataset=dataset)
    h5_obj = H5Object.get(resource_key=h5_key, file=file)
    return json.jsonify(h5_obj)


@app.route('/datadiff/contents/datasets/<dataset_key>/files/<file_key>/h5/<h5_key>/values')
def get_dataset_file_h5_object_values(dataset_key, file_key, h5_key):
    dataset = Dataset.get(dataset_key)
    file = DatasetFile.get(resource_key=file_key, dataset=dataset)
    h5_obj = H5Object.get(resource_key=h5_key, file=file)
    obj_content = h5_obj.get_values(file)
    return json.jsonify(obj_content)


@app.route('/datadiff/comparisons', methods=['POST'])
def api_run_comparison():
    app.logger.info(f'Received request: {request}')
    options = request.get_json()
    app.logger.info(f'Request options: {options}')

    comparison = Comparison.create(
       options=options
    )
    comparison.base = Dataset.get(options['base'])
    comparison.new = Dataset.get(options['new'])

    app.logger.info(f'Created new comparison: {comparison}')
    make_timestamp = datetime.datetime.utcnow

    try:
        comparison.submitted_at = make_timestamp()
        comparison.status = 'started'
        comparator = ModelOutputComparator(
            options,
            output_dir=comparison.path
        )
        comparator.compare(
            comparison.base.path,
            comparison.new.path
        )
    except Exception as e:
        app.logger.critical('Could not run the comparison')
        app.logger.exception(e)
        comparison.outcome = 'error'
    else:
        app.logger.info(f'Comparison {comparison.resource_key} completed successfully')
        comparison.outcome = 'success'
    finally:
        comparison.status = 'completed'
        comparison.completed_at = make_timestamp()
        comparison.save()

    return json.jsonify(comparison)


@app.route('/datadiff/comparisons', methods=['GET'])
def get_comparisons():
    comparisons = list(Comparison.all())
    return json.jsonify(comparisons)


@app.route('/datadiff/comparisons/<key>', methods=['GET'])
def get_comparison(key):
    return json.jsonify(Comparison.get(key))


@app.route('/datadiff/comparisons/<key>/results', methods=['GET'])
def get_comparison_results(key):
    comparison = Comparison.get(key)
    chart_path = comparison.path / 'chart.json'
    return chart_path.read_text()


@app.route('/hello')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
