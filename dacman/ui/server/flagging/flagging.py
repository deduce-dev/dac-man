import os
import shutil
import math
import glob
import uuid
import zipfile
import pickle
import subprocess
import pandas as pd
from collections import defaultdict
from posixpath import join
from pathlib import Path


def frontend_format(data):
    #print("frontend_format.data:", data)
    #print("frontend_format.data['datetime']:", data['datetime'])
    data_dict = data.to_dict(orient='split')

    #print("frontend_format.data_dict:", data_dict)

    cols = []
    datasetVars = []
    for i, col in enumerate(data_dict['columns']):
        #print("data.dtypes[i]:", data.dtypes[i])
        #print("col:", col, "- is_numeric:", data[col].str.isnumeric().any())
        #if str(data.dtypes[i]) == 'object':
        if data[col].astype(str).str.isnumeric().any():
            cols.append({'field': col})
            datasetVars.append({
                'varName': col,
                'contentType': "float"
            })
        else:
            cols.append({'field': col, 'width': 175})
            datasetVars.append({
                'varName': col,
                'contentType': 'string'
            })

    rows = []
    for i, row in enumerate(data_dict['data'], start=1):
        clean_row = {'id': i}
        for j, element in enumerate(row):
            if isinstance(element, float) and math.isnan(element):
                clean_row[cols[j]['field']] = str(element)
            else:
                clean_row[cols[j]['field']] = element
        rows.append(clean_row)
    
    formatted_data = {
        'columns': cols,
        'rows': rows,
        'datasetVars': datasetVars
    }

    return formatted_data

def read_csv(file_path):
    """Read the csv file and return the data"""
    data = pd.read_csv(file_path, na_filter=False)
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    return data

def sample_data(data, n=100):
    formatted_data = frontend_format(data.head(n))

    return formatted_data, data.shape

def load_metadata(pickle_file):
    """Load saved the picked metadata or return an empty one"""
    metadata = defaultdict(set)
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as f:
            unpickler = pickle.Unpickler(f)
            # if file is not empty scores will be equal
            # to the value unpickled
            metadata = unpickler.load()
    
    return metadata

def load_all_metadata(pickle_folder):
    """Load saved the picked metadata or return an empty one"""
    assert os.path.exists(pickle_folder), "Metadata folder doesn't exist"

    metadata = defaultdict(set)

    metadata_files = next(os.walk(pickle_folder))[2]

    print("metadata_files:", metadata_files)

    print("loading all metadata")
    for metadata_file in metadata_files:
        with open(os.path.join(pickle_folder, metadata_file), 'rb') as f:
            unpickler = pickle.Unpickler(f)
            # if file is not empty scores will be equal
            # to the value unpickled
            curr_metadata = unpickler.load()
            print("curr_metadata:", curr_metadata)
            for k, v in curr_metadata.items():
                if len(metadata[k]) == 0:
                    metadata[k] = v
                else:
                    metadata[k] = metadata[k].union(v)

    return metadata

def save_metadata(data_columns, filename, project_path):
    """Iterate through each file and save their accompanied files."""
    pickle_folder = os.path.join(project_path, "metadata/")
    pickle_file = os.path.join(pickle_folder, "metadata_%s.pkl" % uuid.uuid4())
    
    # No more loading. This was stopped because it introduced an error having
    # multiple threads try to load and save to the same file.
    # metadata = load_metadata(pickle_file)

    if not os.path.exists(pickle_folder):
        try:
            os.mkdir(pickle_folder)
        except FileExistsError:
            pass

    metadata = defaultdict(set)

    # for each variable add the file that contains it to the variable's set
    for col in data_columns:
        metadata[col].add(filename)

    with open(pickle_file, 'wb') as f:
        pickle.dump(metadata, f, protocol=4)

# def check_if_similar_vars(datasets_dir):
#     csv_files = glob.glob(os.path.join(datasets_dir, "*.csv"))

def qa_flagging_app_deploy(project_id, datasets_dir, vars_details, results_folder):
    """
    This is core of the flagging application where the command get built and
    run by the subprocess library.

    Run the Rscript command is a format that looks like this:
    $ Rscript qa_n_s.R -f /project/QA_no_seasonal/AirportData_2008-2019_v3.csv -v TEMP_F -n -d --is_numeric -s 3 -t 1.5 -e 3 -b 0,90 -o amo.csv
    """
    # load the saved pickled metadata
    pickle_folder = os.path.join(datasets_dir, "metadata")
    metadata = load_all_metadata(pickle_folder)

    print("all metadata:", metadata)

    output_folder = os.path.join(results_folder, project_id)
    os.mkdir(output_folder)

    var_names = vars_details['varNames']
    flagging_details = vars_details['flaggingDetails']
    for i, details in enumerate(flagging_details):
        # Build the Rscript command-line
        app_args = []
        variable_type = details['variable_type']
        if variable_type == 'numeric':
            app_args.append('--is_numeric')

            if details['checkDuplicates']['checked']:
                app_args.extend(['-s', str(details['checkDuplicates']['subsequentNum'])])
            if details['checkBadVals']['checked']:
                app_args.extend([
                    '-b',
                    '%d,%d' % (
                        details['checkBadVals']['range']['low'],
                        details['checkBadVals']['range']['high'],
                    )
                ])
            if details['checkOutlierVals']['checked']:
                app_args.extend(['-t', str(details['checkOutlierVals']['iqrCoef'])])
            if details['checkExtremeVals']['checked']:
                app_args.extend(['-e', str(details['checkExtremeVals']['iqrCoef'])])
        elif variable_type == 'date':
            app_args.append('--is_date')

        if details['checkNull']:
            app_args.append('-n')

        if details['nullValues']:
            null_values = []

            for val in details['nullValues']:
                if val[0] == '-':
                    # Only the changing the first occurrence so we can pass
                    # it as an argument to the bash command
                    null_values.append(val.replace('-', '*', 1))
                else:
                    null_values.append(val)
            print("null_values:", null_values)
            app_args.extend([
                '-u',
                ','.join(null_values)
            ])

        if details['checkDuplicates']['checked']:
            app_args.append('-d')

        #print(*app_args)

        deduce_backend_path = os.environ.get(
            'DEDUCE_BACKEND_PATH',
            '/home/deduce/workspace'
        )
        r_script_path = os.path.join(deduce_backend_path,
            'dac-man/dacman/ui/server/flagging/r_scripts/qa_n_s.R')

        # Here we iterate through the variables and their accompanied
        # files.

        # Find the related files that need to be processed.
        # Update: This used to process all the files that were uploaded. Now
        # we will only include the files that have the current variable (or
        # `var_name[i]`)

        ############# LEGACY CODE ##############
        #dataset_files = []
        # for f in os.listdir(datasets_dir):
        #     if os.path.isfile(os.path.join(datasets_dir, f)):
        #         dataset_files.append(f)
        #############     END     ##############

        var_name = var_names[i]
        print("var_name:", var_name)
        dataset_files = []
        for dataset_file in metadata[var_name]:
            dataset_files.append(dataset_file)
        
        output_file = '%d.csv' % i
        app_args.extend(['-o', 'x'])
        
        print("dataset_files:", dataset_files)
        # Iterate through the files
        for dataset_name in dataset_files:
            # x -> replaced with the new output flagging file
            dataset_name_no_ext = os.path.splitext(dataset_name)[0]
            dataset_output_path = str(os.path.join(output_folder, dataset_name_no_ext))
            if not os.path.exists(dataset_output_path):
                os.mkdir(dataset_output_path)

            app_args[-1] = str(os.path.join(dataset_output_path, output_file))
            completedProcess = subprocess.run([
                "Rscript",
                r_script_path,
                "-f", str(os.path.join(datasets_dir, dataset_name)),
                "-v", var_names[i],
                *app_args
            ], capture_output=True)

            print(completedProcess)

    return output_folder

def combine_csv_files(csv_folder):
    print("csv_folder:", csv_folder)

    dataset_dirs = next(os.walk(csv_folder))[1]

    print("dataset_dirs:", dataset_dirs)

    assert len(dataset_dirs) != 0, "No dataset folders to process"

    first_dataset_name = None
    for dataset_dir in dataset_dirs:
        if first_dataset_name is None:
            first_dataset_name = dataset_dir
        dataset_name = dataset_dir
        csv_files = glob.glob(os.path.join(csv_folder, dataset_name, "*.csv"))
        df_list = []
        print("dataset_name:", dataset_name, "csv_files:", csv_files)
        for csv_file in csv_files:
            df = pd.read_csv(csv_file, na_filter=False)
            df_list.append(df)
            # delete numbered file
            os.remove(csv_file)

        df_all = pd.concat(df_list, axis=1)

        #compression_opts = dict(
        #    method='zip',
        #    archive_name='flagged_variables.csv'
        #)

        output_csv_file = os.path.join(csv_folder, dataset_name + "_flagged.csv")
        #output_zip_file = os.path.join(csv_folder, "flagged_variables.csv.gz")

        #### old
        #output_zip_file = os.path.join(csv_folder, "flagged_variables.zip")

        df_all.to_csv(
            output_csv_file,
            index=False
        )

    csv_unifed_files = glob.glob(os.path.join(csv_folder, "**/*.csv"), recursive=True)

    print("csv_unifed_files:", csv_unifed_files)

    combined_datasets_name = '_'.join(dataset_dirs)[:50]
    output_csv_file = os.path.join(csv_folder, first_dataset_name + '_flagged.csv')

    #output_zip_file = os.path.join(csv_folder, first_dataset_name + '.zip')
    output_zip_file = os.path.join(csv_folder, combined_datasets_name + '.zip')

    print("output_zip_file:", output_zip_file)

    with zipfile.ZipFile(output_zip_file, 'w') as zf:
        for file in csv_unifed_files:
            zf.write(file, os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)

    return output_csv_file, output_zip_file
    #return output_zip_file

def clean_up(folder):
    if os.path.exists(folder) and os.path.isdir(folder):
        shutil.rmtree(folder)
    else:
        raise ValueError("Folder argument either doesn't exist or isn't a folder")

