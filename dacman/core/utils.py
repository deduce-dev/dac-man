"""
`dacman.core.utils`
====================================

.. currentmodule:: dacman.core.utils

:platform: Unix, Mac
:synopsis: Module containing several utility functions

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

import yaml
import os
import time
import hashlib

DACMAN_STAGING_LOC = os.path.join(os.getenv('HOME'), '.dacman/data')

def dump_yaml(data, filepath):
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    

def update_yaml(data, filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            orig_data = yaml.load(f)
            for new_val in data:
                if new_val in orig_data:
                    for old_val in data[new_val]:
                        orig_data[new_val][old_val] = data[new_val][old_val]
                else:
                    orig_data[new_val] = data[new_val]
            dump_yaml(orig_data, filepath)
    else:
        dump_yaml(data, filepath)


def load_yaml(yaml_file):
    with open(yaml_file, 'r') as f:
        data = yaml.load(f)
        return data        


def cprint(caller, str):
    #print("[{}] [{}] {}".format(time.time(), caller, str))
    pass
    

def dict_to_file(data, filepath):
    with open(filepath, 'w') as f:
        for key in data:
            line = '{}: {}\n'.format(key, data[key])
            f.write(line)


def list_to_file(data, filepath):
    with open(filepath, 'w') as f:
        for elem in data:
            line = '{}\n'.format(elem)
            f.write(line)


def file_to_dict(filename):
    dict_data = {}
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            kv = line.split(':')            
            key = kv[0].strip()
            dict_data[kv[0].strip()] = kv[1].strip()
    return dict_data


def file_to_dict_list(filename):
    dict_data = {}
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            kv = line.split(':')            
            key = kv[0].strip()
            values = kv[1].split()
            dict_data[key] = values
    return dict_data


def hash_comparison_id(old_path, new_path):
   hash = hashlib.md5('{}{}'.format(old_path, new_path).encode('utf-8')).hexdigest()
   return hash


def get_hash_id(path):
   hash = hashlib.md5(path.encode('utf-8')).hexdigest()
   return hash


def get_nfiles(path, stagingdir):
    scan_file = os.path.join(stagingdir, 'indexes', get_hash_id(path), 'FILEPATHS')
    with open(scan_file) as f:
        nlines = sum(1 for line in f)
    return nlines
