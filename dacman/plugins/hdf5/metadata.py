#!/usr/bin/env python3.6

from pathlib import Path
import collections
import json

import h5py as h5
import numpy as np


def collect_from_obj(d, name=None, obj=None):

    d['name'] = name
    d['id'] = obj.id.id
    d['attributes'] = dict(obj.attrs)
    d['type_h5'] = type(obj).__name__
    d['type_h5py'] = type(obj)

    d['name_parent'] = obj.parent.name
    # stem = name without the parent (following `pathlib.Path`)
    d['name_stem'] = d['name'].replace(d['name_parent'], '').strip('/')


def collect_from_dataset(d, dataset):

    d['name'] = dataset.name
    d['shape'] = dataset.shape
    d['ndim'] = dataset.ndim

    try:
        dtype = dataset.dtype
    except Exception as e:
        dtype = None
        d['dtype_error'] = str(e)

    d['dtype'] = dtype


def collect_from_dataset_value(d, dataset):

    value =  dataset[()]

    d['type_value'] = type(value)
    d['value'] = value


def collect_from_group(d, group):

    counter = collections.Counter(type(obj).__name__ for obj in group.values())

    id_ = group.id

    d['fileno'] = id_.fileno
    d['num_objs'] = dict(counter)
    d['num_objs']['total'] = id_.get_num_objs()

def collect_from_file(d, file):
    d['filename'] = file.filename


class ObjMetadataCollector:
    """
    Collect metadata from a single h5 Object.
    """

    def __init__(self, *, obj=None, name=None, collect_dataset_values=True):
        
        self.obj = obj
        self.name = name

        self.collect_dataset_values = collect_dataset_values

        self._data = {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, val):
        self._data[key] = val

    def keys(self):
        return self._data.keys()

    @property
    def is_dataset(self):
        return isinstance(self.obj, h5.Dataset)

    @property
    def is_group(self):
        return isinstance(self.obj, h5.Group)

    @property
    def is_file(self):
        return isinstance(self.obj, h5.File)

    def collect(self):

        collect_from_obj(self, obj=self.obj, name=self.name)

        if self.is_dataset:
            self['dataset'] = {}
            collect_from_dataset(self['dataset'], self.obj)
            if self.collect_dataset_values:
                collect_from_dataset_value(self['dataset'], self.obj)

        if self.is_group:
            self['group'] = {}
            collect_from_group(self['group'], self.obj)

        if self.is_file:
            self['file'] = {}
            collect_from_file(self['file'], self.obj)


class RecursiveMetadataCollector:
    """
    Collect metadata for Objects. For Files or Groups, recursively collect metadata from all contained objects.
    """

    def __init__(self, obj, name=None, collect_dataset_values=True):

        self.obj = obj
        self.name = name or self.obj.name

        self.collect_dataset_values = collect_dataset_values

        self._items = []

    def __iter__(self):
        return iter(self._items)

    def add(self, props):
        self._items.append(props)

    def visit(self, name, obj):

        metadata = ObjMetadataCollector(obj=obj, name=name, collect_dataset_values=self.collect_dataset_values)

        metadata.collect()

        self.add(dict(metadata))

    def collect(self):

        # collect root object for all types:
        self.visit(self.name, self.obj)

        # collect recursively for containers (File, Group)
        try:
            self.obj.visititems(self.visit)
        except AttributeError:
            pass


def main():
    import sys
    # TODO this import here is a possible cause of import errorss/warnings
    from .util import to_json

    args = sys.argv[1:]

    path_in = args[0]

    try:
        obj_name = args[1]
    except IndexError:
        obj_name = None

    mode_read_only = 'r'
    collect_opts = {'collect_dataset_values': False}
    try:
        file = h5.File(path_in, mode_read_only)
        obj = file[obj_name] if obj_name else file
        collector = RecursiveMetadataCollector(obj, **collect_opts)
        collector.collect()
        print(to_json(list(collector)))

    except Exception as e:
        print(f'Error: {repr(e)}', file=sys.stderr)
        sys.exit(1)
    finally:
        file.close()

        
if __name__ == '__main__':
    main()
