"""
Analyze differences between output files of ED2 models.
"""

from dataclasses import dataclass
import logging
import os
import uuid
from pathlib import Path
import re
import tarfile
import typing as t

from pydantic  import BaseModel
import numpy as np
import pandas as pd
import h5py
import altair as alt
import tqdm

from flask import Flask, flash, request, redirect
from flask import render_template, json, send_from_directory, send_file, url_for
from flask_cors import CORS

from dacman.compare import base


app = Flask(__name__, static_folder='../fits/build/static', template_folder='../fits/build')
CORS(app, supports_credentials=True)
app.config['JSON_SORT_KEYS'] = False

_logger = app.logger


class Options(BaseModel):
    sample_fields: t.List[str] = []
    max_n_files: int = -1


app.config['DATASETS_DIR'] = Path('/tmp/deduce/datasets')
app.config['COMPARISONS_DIR'] = Path('/tmp/deduce/comparisons')


class CompositeFieldKey:
    field_sep = ':'
    index_sep = ','

    def __init__(
            self,
            field: str,
            component_index: t.Union[int, t.Tuple[int]]
        ):
        self.field = field
        self.component_index = component_index

    def __repr__(self):
        return f'<{self.__class__.__name__}(field={self.field}, index={self.component_index})>'

    def __str__(self):
        try:
            idx_to_join = tuple(self.component_index)
        except TypeError:
            idx_to_join = tuple([self.component_index])

        str_idx = str.join(
            self.index_sep,
            [str(dim_idx) for dim_idx in idx_to_join]
        )
        return f'{self.field}{self.field_sep}{str_idx}'

    @classmethod
    def from_str(cls, s):
        field, str_idx = s.split(cls.field_sep)
        component_index = tuple(int(i) for i in str_idx.split(cls.index_sep))
        if len(component_index) == 1:
            component_index = component_index[0]

        return cls(
            field,
            component_index
        )

    @classmethod
    def get(cls, other):
        if isinstance(other, cls):
            return other
        return cls.from_str(other)

    @classmethod
    def get_iter(cls, other_iterable):
        for other in other_iterable:
            yield cls.get(other)


def extract_keys(file: h5py.File, field=None):
    fields = [field] if field is not None else file.keys()
    for field in fields:

        dataset = file[field]
        data = dataset[:]
        for idx, value in np.ndenumerate(data):
            key = CompositeFieldKey(
                field=field,
                component_index=idx
            )
            yield key


def get_h5_values_data(file: h5py.File, keys=None):
    out_data = {}

    if keys is None:
        keys = extract_keys(file)
    for key in CompositeFieldKey.get_iter(keys):
        dataset = file[key.field]
        arr = dataset[:]
        # print(f'arr={arr}')
        # TODO maybe here we don't need the intermediate [:]
        value = arr[key.component_index]
        # TODO here we're converting everything to float but we might need something more general
        value_out = None if np.isnan(value) else float(value)

        out_data[str(key)] = value_out

    return out_data


def get_h5_fields_metadata(file: h5py.File):
    out_data = []
    for h5_key in file.keys():
        dataset = file[h5_key]
        out_data.append({
            'name': h5_key,
            'type': repr(dataset)
        })
    return out_data


def get_sample_info(path: Path):
    """Get information from sample file to use for e.g. populating options in UI"""
    d = {
        'fields': [],
        'values': {},
    }
    with h5py.File(path, 'r') as f:
        d['fields'] = get_h5_fields_metadata(f)
        d['values'] = get_h5_values_data(f)

    return d


def get_options():
    import json
    with Path('options.json').open() as f:
        data = json.load()
    return data


@app.route('/datadiff/content/<resource>')
def api_get_sample_info(resource):
    data = request.args
    if resource == 'dir':
        datasets = [str(p) for p in app.config['DATASETS_DIR'].glob('*') if p.is_dir()]
        content = datasets
    if resource == 'file':
        dir_ = data.get('dir')
        limit = int(data.get('limit', 100))
        all_paths = [str(p.name) for p in sorted(Path(dir_).glob('*.h5'))]
        content = all_paths
        try:
            content = all_paths[:limit]
        except IndexError:
            pass
        print(f'content={content}')
    if resource == 'h5':
        dir_ = data.get('dir')
        file_name = data.get('file')
        # path = Path("/home/ludo/lbl/nosync/deduce/tlpowell/ED2/test68") / "BCI_Xu-E-1300-01-00-000000-g01.h5"
        sample_file_path = Path(dir_) / file_name
        app.logger.info(f'sample_file_path={sample_file_path}')
        content = get_sample_info(sample_file_path)
    resp = json.jsonify(content)
    return resp

    # sample_info = get_sample_info(path)


@app.route('/datadiff/comparison', methods=['POST'])
def api_run_comparison():
    comparison_id = str(uuid.uuid4())
    output_dir = app.config['COMPARISONS_DIR'] / comparison_id
    print(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(request)
    options = request.get_json()
    print(options)
    path_v1, path_v2 = [Path(p) for p in options['paths']]
    resp_data = dict(
        outcome=None,
        comparison_id=None,
    ) 
    try:
        comparator = ModelOutputComparator(options, output_dir=output_dir)
        comparator.compare(path_v1, path_v2)
    except Exception as e:
        app.logger.critical('Could not run the comparison')
        app.logger.exception(e)
        resp_data.update(outcome='error')
    else:
        resp_data.update(
            outcome='success',
            comparison_id=comparison_id
        )
        # return send_from_directory(output_dir, 'chart.html')
    resp = json.jsonify(resp_data)
    return resp


@app.route('/datadiff/comparison/', methods=['GET'])
def get_comparisons():
    cmp_dir = app.config['COMPARISONS_DIR']
    ids = [p.name for p in cmp_dir.glob('*')]
    data = [
        {
            'comparison_id': id_,
            'results_url': url_for('get_comparison', comparison_id=id_),
            # TODO save and add other comparison metadata
        }
        for id_ in ids
    ]
    resp = json.jsonify(data)
    return resp


@app.route('/datadiff/comparison/<comparison_id>', methods=['GET'])
def get_comparison(comparison_id):
    cmp_dir = app.config['COMPARISONS_DIR'] / comparison_id
    resp = send_file(cmp_dir / 'chart.html')
    return resp


def untar(src_path: Path, dst_path: Path):
    assert src_path.exists, "The source path should exist"
    # TODO what should we do with dst_path? how should we deal with it if e.g. it already exists?
    try:
        with tarfile.open(src_path, 'r') as tf:
            tf.extractall(path=dst_path)
    except Exception as e:
        _logger.error(f'Could not untar file {src_path} into destination directory {dst_path}')
        _logger.exception(e)
    else:
        _logger.info(f'File {src_path} extracted successfully into {dst_path}')


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


@app.route('/datadiff/upload', methods=['POST'])
def process_upload():
    tmp_path = Path('/tmp/uploaded_file')

    dataset_id = uuid.uuid4()
    base_dir = app.config['DATASETS_DIR']
    base_dir.mkdir(parents=True, exist_ok=True)

    final_dir = base_dir / str(dataset_id)
    try:
        app.logger.info(f'Starting to save uploaded stream to {tmp_path}')
        write_stream(request.stream, tmp_path)
        app.logger.info(f'size=({tmp_path.stat().st_size}')
        app.logger.info(f'Trying to untar the uploaded file into {final_dir}')
        untar(tmp_path, final_dir)
        app.logger.info(f'Removing temporary file')
        tmp_path.unlink()
    except Exception as e:
        app.logger.error('Operation failed')
        app.logger.exception(e)
    else:
        app.logger.info(f'Operation complete')
        return 'OK'


class ModelOutputFileData:
    """
    Represent data to compare for a single model output file.
    """
    name_regex_pattern = 'BCI_Xu-E-(?:(?P<year>\d{4})-(?P<month>\d{2})-\d{2}-\d{6})-g01'

    def __init__(self,
            file: h5py.File,
            path: Path = None,
            keys=None,
            name_regex_pattern=None
        ):
        self.file = file
        self.path = path or Path(file.filename)
        self.keys = keys
        self.name_regex_pattern = name_regex_pattern or type(self).name_regex_pattern

    @property
    def timestamp(self) -> pd.Period:
        pattern = self.name_regex_pattern
        to_parse = self.path.stem
        match = re.match(pattern, to_parse)
        if match:
            d = match.groupdict()
            # return pd.Period instead of pd.Timestamp because time range falls outside of representable date range
            return pd.Period(
                year=int(d['year']),
                month=int(d['month']),
                freq='M'
            )

    @property
    def h5_values(self):
        values = get_h5_values_data(
            self.file,
            keys=self.keys
        )

        return values

    def to_dict(self):
        d = {
            'timestamp': self.timestamp,
        }
        d.update(self.h5_values)

        return d


class ModelOutputDatasetChangeMetrics:

    def __init__(
            self,
            a: pd.DataFrame,
            b: pd.DataFrame,
            index_field: str = None,
            fields: t.List[str] = None,
        ):
        self.a = self.set_index(a, index_field)
        self.b = self.set_index(b, index_field)
        self.index_field = index_field
        self.fields = fields or list(self.a.columns)

    def set_index(self, df: pd.DataFrame, field: str) -> pd.DataFrame:
        return (
            df
            .reset_index(drop=True)
            .set_index(field)
            .sort_index()
        )

    @property
    def difference(self) -> pd.DataFrame:
        d = {}
        for field in self.fields:
            # TODO add try/except if a field dtype does not support "-"
            d[field] = self.b[field] - self.a[field]
        return pd.DataFrame(d)

    def to_long_format(self, df: pd.DataFrame, field: str) -> pd.DataFrame:
        "Convert dataframe from 'wide' to 'long' format"
        return (
            df
            .reset_index()
            .melt(
                self.index_field,
                var_name='observable',
                value_name=field,
            )
            .set_index(self.index_field)
        )

    @property
    def long(self) -> pd.DataFrame:
        return (
            self.to_long_format(
                self.difference, 'difference'
            )
            .assign(
                v1=self.to_long_format(self.a, 'v1')['v1'],
                v2=self.to_long_format(self.b, 'v2')['v2'],
            )
        )

    @property
    def for_plotting(self) -> pd.DataFrame:
        return (
            self.long
            .reset_index()
            .astype({'timestamp': str})
        )


class ModelOutputComparator(base.Comparator):

    @staticmethod
    def supports():
        return ['h5']

    @staticmethod
    def description():
        return ""

    def stats(self):
        pass

    def percent_change(self):
        pass

    default_options = {
        'fields': [
            "MMEAN_GPP:0",
            "AGB_PFT:0,1",
            "AGB_PFT:0,3",
            "AGB_PFT:0,24",
            "AGB_PFT:0,25",
        ],
        'max_n_files': 5000
    }

    def __init__(self,
            options: dict = None,
            field_keys: t.Optional[t.Iterable] = None,
            output_dir: Path = None,
        ):
        options = options or {}
        self.options = dict(type(self).default_options)
        self.options.update(options)

        self.field_keys = field_keys or self.options['fields']
        self.output_dir = Path(output_dir or '.')

    def load_dataset(self, path: Path) -> pd.DataFrame:
        _logger.info('Loading dataset "%s"', path)
        paths_to_load = list(sorted(Path(path).glob('*.h5')))
        _logger.info(f'Found {len(paths_to_load)} HDF5 files')
        n_files = self.options['max_n_files']
        # paths_to_load = tqdm.tqdm(list(paths_to_load)[:n_files])
        paths_to_load = paths_to_load[:n_files]
        single_file_data_items = []

        for file_path in paths_to_load:
            _logger.info(f'Processing path: {str(file_path)}')

            with h5py.File(file_path, 'r') as h5_file:
                file_data = ModelOutputFileData(
                    h5_file,
                    keys=self.field_keys
                )
                file_data_out = file_data.to_dict()
                single_file_data_items.append(file_data_out)

        df = pd.DataFrame(single_file_data_items)
        return df

    def get_metrics(self, data_v1, data_v2):
        return ModelOutputDatasetChangeMetrics(
            data_v1,
            data_v2,
            fields=self.options['fields'],
            index_field='timestamp'
        )

    def compare(self, path_v1, path_v2):
        _logger.info('Starting comparison')
        data_v1 = self.load_dataset(path_v1)
        data_v2 = self.load_dataset(path_v2)
        _logger.info('Calculating change metrics')
        metrics = self.get_metrics(data_v1, data_v2)
        _logger.info('Creating change analysis chart')
        chart = self.get_chart(metrics.for_plotting)
        _logger.info('Saving change analysis results')
        self.save(chart)

    @property
    def chart_properties(self) -> dict:
        return dict(
            width=800,
            height=250,
        )

    def get_line_chart(self, data: pd.DataFrame, selection) -> alt.Chart:
        return (
            alt.Chart(
                data
            )
            .mark_line()
            .encode(
                x=f'timestamp:T',
                y='difference',
                color='observable',
                tooltip=list(data.columns),
                opacity=alt.condition(selection, alt.value(1), alt.value(0))
            )
            .add_selection(selection)
        )

    def get_hist_chart(self, data: pd.DataFrame, selection) -> alt.Chart:
        return (
            alt.Chart(data)
            .mark_area(
                interpolate='step'
            )
            .encode(
                alt.X('difference:Q', bin=alt.Bin(maxbins=100)),
                alt.Y('count()', stack=None),
                color=alt.Color('observable:N'),
                tooltip=['observable', 'count()'],
                opacity=alt.condition(selection, alt.value(0.8), alt.value(0)),
            )
            .add_selection(selection)
        )

    def get_chart(self, data) -> alt.Chart:
        selection = alt.selection_multi(fields=['observable'], bind='legend')
        lines = self.get_line_chart(data, selection).properties(**self.chart_properties)
        hists = self.get_hist_chart(data, selection).properties(**self.chart_properties)
        return (lines & hists)

    def save(self, chart: alt.Chart, file_name='chart.html') -> Path:
        path = self.output_dir / file_name
        chart.save(str(path))
        return path


def main():
    _logger.setLevel(logging.DEBUG)

    with Path('options.json').open() as f:
        options = json.load(f)
    path_v1 = Path(options['paths']['v1'])
    path_v2 = Path(options['paths']['v2'])

    sample_file = options.get("sample_file")
    if sample_file:
        sample_file_path = path_v1 / sample_file
        sample_info = get_sample_info(sample_file_path)
        sample_info['choices'] = {
            'dir': {
                'A': [str(path_v1)],
                'B': [str(path_v2)]
            },
            'sample_file': [str(sample_file_path)],
            'analysis_type': ['new - base'],
            'visualization_type': ['histogram']

        }
        with Path("sample.json").open("w") as f:
            json.dump(sample_info, f, indent=4)

    else:
        comparator = ModelOutputComparator(options)
        comparator.compare(path_v1, path_v2)


if __name__ == "__main__":
    main()
