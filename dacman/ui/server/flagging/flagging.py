import os
import shutil
import math
import glob
import subprocess
import uuid
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

def read_csv(file_path):
    data = pd.read_csv(file_path, na_filter=False)
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    print(data)
    formatted_data = frontend_format(data.head(10))

    return formatted_data

def qa_flagging_app_deploy(dataset, vars_details, results_folder):
    # Rscript qa_n_s.R -f /project/QA_no_seasonal/AirportData_2008-2019_v3.csv -v TEMP_F -n -d --is_numeric -s 3 -t 1.5 -e 3 -b 0,90 -o amo.csv
    
    output_folder = os.path.join(results_folder, str(uuid.uuid4()))
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

        output_file = '%d.csv' % i
        app_args.extend(['-o', str(os.path.join(output_folder, output_file))])

        print(*app_args)
        completedProcess = subprocess.run([
            "Rscript",
            "flagging/r_scripts/qa_n_s.R",
            "-f", dataset,
            "-v", var_names[i],
            *app_args
        ], capture_output=True)

        print(completedProcess)

    return output_folder

def combine_csv_files(csv_folder):
    print("csv_folder", csv_folder)
    csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))
    df_list = []
    print(csv_files)
    for csv_file in csv_files:
        df = pd.read_csv(csv_file, na_filter=False)
        df_list.append(df)

    df_all = pd.concat(df_list, axis=1)

    compression_opts = dict(
        method='zip',
        archive_name='flagged_variables.csv'
    )

    output_csv_file = os.path.join(csv_folder, "flagged_variables.csv")
    output_zip_file = os.path.join(csv_folder, "flagged_variables.zip")

    df_all.to_csv(
        output_csv_file,
        index=False
    )
    df_all.to_csv(
        output_zip_file,
        index=False,
        compression=compression_opts
    )

    return output_csv_file, output_zip_file

def clean_up(folder):
    if os.path.exists(folder) and os.path.isdir(folder):
        shutil.rmtree(folder)
    else:
        raise ValueError("Folder argument either doesn't exist or isn't a folder")

