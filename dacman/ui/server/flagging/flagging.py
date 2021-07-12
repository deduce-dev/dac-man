import os
import shutil
import math
import glob
import zipfile
#import gzip
import subprocess
import pandas as pd


def frontend_format(data):
    data_dict = data.to_dict(orient='split')

    cols = []
    datasetVars = []
    for i, col in enumerate(data_dict['columns']):
        if str(data.dtypes[i]) == 'object':
            cols.append({'field': col, 'width': 175})
            datasetVars.append({
                'varName': col,
                'contentType': 'string'
            })
        else:
            cols.append({'field': col})
            datasetVars.append({
                'varName': col,
                'contentType': str(data.dtypes[i])
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

def sample_data(file_path, n=100):
    data = pd.read_csv(file_path, na_filter=False)
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]

    formatted_data = frontend_format(data.head(n))

    return formatted_data, data.shape

def check_if_similar_vars(datasets_dir):
    csv_files = glob.glob(os.path.join(datasets_dir, "*.csv"))


def qa_flagging_app_deploy(project_id, datasets_dir, vars_details, results_folder):
    # Rscript qa_n_s.R -f /project/QA_no_seasonal/AirportData_2008-2019_v3.csv -v TEMP_F -n -d --is_numeric -s 3 -t 1.5 -e 3 -b 0,90 -o amo.csv
    
    output_folder = os.path.join(results_folder, project_id)
    os.mkdir(output_folder)

    var_names = vars_details['varNames']
    flagging_details = vars_details['flaggingDetails']
    for i, details in enumerate(flagging_details):
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

        if details['checkDuplicates']['checked']:
            app_args.append('-d')

        #print(*app_args)

        deduce_backend_path = os.environ.get(
            'DEDUCE_BACKEND_PATH',
            '/home/deduce/workspace'
        )
        r_script_path = os.path.join(deduce_backend_path,
            'dac-man/dacman/ui/server/flagging/r_scripts/qa_n_s.R')

        dataset_files = []
        for f in os.listdir(datasets_dir):
            if os.path.isfile(os.path.join(datasets_dir, f)):
                dataset_files.append(f)
        
        output_file = '%d.csv' % i
        app_args.extend(['-o', 'x'])

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

        df_all = pd.concat(df_list, axis=1)

        #compression_opts = dict(
        #    method='zip',
        #    archive_name='flagged_variables.csv'
        #)

        output_csv_file = os.path.join(csv_folder, dataset_name + ".csv")
        #output_zip_file = os.path.join(csv_folder, "flagged_variables.csv.gz")

        #### old
        #output_zip_file = os.path.join(csv_folder, "flagged_variables.zip")

        df_all.to_csv(
            output_csv_file,
            index=False
        )

        #df_all.to_csv(
        #    output_zip_file,
        #    index=False,
        #    compression=compression_opts
        #)

        #df_all.to_csv(
        #    output_zip_file,
        #    index=False,
        #    compression='gzip'
        #)

    csv_unifed_files = glob.glob(os.path.join(csv_folder, "*.csv"))

    output_csv_file = os.path.join(csv_folder, first_dataset_name + '.csv')

    #output_zip_file = os.path.join(csv_folder, first_dataset_name + '.csv.gz')
    output_zip_file = os.path.join(csv_folder, first_dataset_name + '.zip')

    #with gzip.open(output_zip_file, 'wb') as f_out:
    #    for file in csv_unifed_files:
    #        with open(file, 'rb') as f_in:
    #            f_out.writelines(f_in)

    with zipfile.ZipFile(output_zip_file, 'w') as zf:
        for file in csv_unifed_files:
            zf.write(file, os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)

    return output_csv_file, output_zip_file

def clean_up(folder):
    if os.path.exists(folder) and os.path.isdir(folder):
        shutil.rmtree(folder)
    else:
        raise ValueError("Folder argument either doesn't exist or isn't a folder")

