import numpy as np
import h5py as h5

from dacman.compare import base

from . import metadata
from .util import to_json, to_dict_basic_types


class DiffStatus:
    added = 'ADDED'
    deleted = 'DELETED'
    modified = 'MODIFIED'
    unchanged = 'UNCHANGED'

    @classmethod
    def iter(cls):
        yield from (cls.added, cls.deleted, cls.modified, cls.unchanged)


class _missing(object):

    def __bool__(self):
        return False


MISSING = _missing()


class Record:
    """
    An indexed collection of metadata items.

    `key_getter`: a function that returns the index key when applied to each metadata item.
    """

    @staticmethod
    def default_key_getter(md):
        return md['name']

    def __init__(self, source=None, collector=None, key_getter=None, **kwargs):

        if collector is None:
            collector = metadata.RecursiveMetadataCollector(source, **kwargs)

        collector.collect()

        metadata_items = collector

        self.key_getter = key_getter or self.default_key_getter

        self._map = {self.key_getter(md): md for md in metadata_items}

    def keys(self):
        return self._map.keys()

    def values(self):
        return self._map.values()

    def items(self):
        return self._map.items()

    def __getitem__(self, key):
        return self._map[key]

    def get(self, *args, **kwargs):
        return self._map.get(*args, **kwargs)

    def display(self, mode='json'):
        if mode == 'json':
            print(to_json(self._map))

    def _ipython_display_(self):
        from IPython.display import display, JSON

        display(JSON(to_dict_basic_types(self._map)))


class ComparisonMetricsBase:
    """
    Convenience class to access properties from items being compared and calculate comparison metrics from them.
    """
    def __init__(self, key, a=None, b=None):
        self.key = key
        self.a = a
        self.b = b

        self._comparison_data = {}
        
    def __setitem__(self, key, val):
        self._comparison_data[key] = val
        
    def __getitem__(self, key):
        return self._comparison_data[key]

    def keys(self):
        # TODO maybe enforce some order?
        return self._comparison_data.keys()
    
    def add(self, other_data):
        self._comparison_data.update(other_data)

    @property
    def properties(self):
        # only interested in common fields, since we have to compare them directly
        return self.a.keys() & self.b.keys()

    @property
    def is_unset_a(self):
        return len(self.a) == 0

    @property
    def is_unset_b(self):
        return len(self.b) == 0

    def change_in(self, prop):
        if prop not in self.properties:
            return False
        try:
            return self.a[prop] != self.b[prop]
        except Exception as e:
            print(e)
            return False

    def get_if_common(self, prop):
        if prop in self.properties and not self.change_in(prop):
            return self.a[prop]
        # maybe use a sentinel value other than None here?
        return None
    
    def get_value_single(self, prop):
        if self.is_unset_a:
            return self.b[prop]
        if self.is_unset_b:
            return self.a[prop]
        return self.get_if_common(prop)

    def get_values(self, prop, orient=dict, convert=None, as_type=None, fallback=None):
        if convert is None and as_type is not None:
            convert = as_type

        convert = convert or (lambda x: x)

        val_a = convert(self.a.get(prop, fallback))
        val_b = convert(self.b.get(prop, fallback))

        if orient in {tuple, list}:
            return val_a, val_b

        if orient in {dict}:
            return {'a': val_a, 'b': val_b}

    # this should go to the individual functions
    def set_values_if_changed(self, prop):
        if self.change_in(prop):
            self[prop] = self.get_values(prop)

    def set_unchanged(self, props):
        for prop in props:
            val = self.get_value_single(prop)
            if val is not None:
                self[prop] = val

    @property
    def is_modified(self):
        # TODO change if we use multiple modified states
        return self['status'] in {DiffStatus.modified}

    @is_modified.setter
    def is_modified(self, val):
        if bool(val) is True:
            # TODO manage other types as extra "modified" characterizers
            # e.g. if `val` is a list, append to self['modified_labels']
            self['status'] = DiffStatus.modified

    def calculate(self):
        raise NotImplementedError


class ObjMetadataMetrics(ComparisonMetricsBase):
    """
    Comparison metrics for generic HDF5 Objects, calculated from metadata properties.
    """

    @property
    def is_changed_type(self):
        return self.change_in('type_h5')

    @property
    def is_changed_attributes(self):
        return self.change_in('attributes')

    @property
    def is_dataset(self):
        return 'dataset' in self.properties
        # return self.get_if_common('type_h5') == "Dataset"

    @property
    def is_group(self):
        return 'group' in self.properties
        # return self.get_if_common('type_h5') in {"Group", "File"}

    @property
    def is_file(self):
        return 'file' in self.properties
        # return self.get_if_common('type_h5') in {"File"}

    def calculate(self):

        self.set_unchanged(['name', 'type_h5'])
        self['status'] = DiffStatus.unchanged

        if self.is_unset_a:
            self['status'] = DiffStatus.added
            self['type_h5'] = self.b['type_h5']

        if self.is_unset_b:
            self['status'] = DiffStatus.deleted
            self['type_h5'] = self.a['type_h5']

        self.calc_for_obj()
        self.calc_for_attributes()

        if self.is_dataset:
            self.calc_for_dataset()

        if self.is_group:
            self.calc_for_group()

        if self.is_file:
            self.calc_for_file()

    def calc_for_obj(self):

        if self.change_in('name'):
            self.is_modified = True
            self['name'] = self.get_values('name')

        if self.is_changed_type:
            self.is_modified = True
            self['type_h5'] = self.get_values('type_h5')

    def calc_for_attributes(self):

        if self.is_changed_attributes:
            self.is_modified = True
            self['attributes'] = self.get_values('attributes')

    def calc_for_dataset(self):

        metrics = DatasetMetadataMetrics(f'{self.key}.dataset', self.a['dataset'], self.b['dataset'])
        metrics.calculate()
        self.add(metrics)

    def calc_for_group(self):
        metrics = GroupMetadataMetrics(f'{self.key}.group', self.a['group'], self.b['group'])
        metrics.calculate()
        self.add(metrics)

    def calc_for_file(self):
        metrics = FileMetadataMetrics(f'{self.key}.file', self.a['file'], self.b['file'])
        metrics.calculate()
        self.add(metrics)


class DatasetMetadataMetrics(ComparisonMetricsBase):
    """
    Comparison metrics for Datasets, using metadata properties.
    """

    @property
    def is_changed_ndim(self):
        return self.change_in('ndim')

    @property
    def is_changed_shape(self):
        return self.change_in('shape')

    @property
    def is_changed_dtype(self):
        return self.change_in('dtype')

    @property
    def is_changed_value(self):
        return self.change_in('value')

    def calculate(self):

        if self.is_changed_ndim:
            self.is_modified = True
            self['ndim'] = self.get_values('ndim')
        if self.is_changed_shape:
            self.is_modified = True
            self['shape'] = self.get_values('shape')
        if self.is_changed_dtype:
            self.is_modified = True
            self['dtype'] = self.get_values('dtype')
            # this doesn't actually make much sense
            # if not self.is_changed_shape:
                # only store the value when the shape is the same, i.e. when only the dtype changes
                # self['value'] = self.get_dataset_values()

        if not any([self.is_changed_ndim, self.is_changed_shape, self.is_changed_dtype]):
            self.calc_for_value()

    def calc_for_value(self):
        dset_a, dset_b = self.get_values('dataset_obj', orient=tuple)

        # first assume that the Datasets are arrays
        # (we know that the shape is the same, so we can assume that this applies to both)
        try:
            val_a, val_b = [dset[:] for dset in (dset_a, dset_b)]
            vals_eq = np.array_equal(val_a, val_b)
        except (ValueError, TypeError):
            # the content of the Datasets are scalars
            val_a, val_b = [dset[()] for dset in (dset_a, dset_b)]
            vals_eq = val_a == val_b

        if not vals_eq:

            self.is_modified = True
            self['value'] = {'a': val_a, 'b': val_b}

            try:
                # TODO an additional check on dtype is needed here
                # to exclude those for which elementwise difference doesn't make sense
                self['delta_elementwise'] = val_a - val_b
                self['delta_mean'] = np.mean(self['delta_elementwise'])
            except TypeError:
                pass


class GroupMetadataMetrics(ComparisonMetricsBase):
    """
    Comparison metrics for Datasets, using metadata properties.
    """

    @property
    def is_changed_num_objs(self):
        return self.change_in('num_objs')
    
    def calculate(self):

        if self.is_changed_num_objs:
            self.is_modified = True
            nums_a, nums_b = self.get_values('num_objs', orient=tuple)
            self['num_objs'] = {
                'a': nums_a,
                'b': nums_b,
            }


class FileMetadataMetrics(ComparisonMetricsBase):
    
    def calculate(self):
        print(self.get_values('filename'))
        if self.change_in('filename'):
            self.is_modified = True
            self['filename'] = self.get_values('filename')


# TODO this should eventually inherit from dacman.Comparator
class HDF5Plugin(base.Comparator):
    """
    Dac-man plug-in to compare HDF5 files, using information from metadata collected from the contained Objects.
    """

    @staticmethod
    def supports():
        return ['h5']

    @classmethod
    def description(cls):
        return cls.__doc__

    def __init__(self):
        # this is stateful, even though it shouldn't be, 
        # because the comparees are given as args to compare() and not as attributes to __init__()).
        self._metrics = []

    @staticmethod
    def record_key_getter(metadata):
        return metadata['name']

    def get_metadata_collector(self, *args, **kwargs):
        return metadata.RecursiveMetadataCollector(*args, **kwargs)

    def get_record(self, file, obj_name=None):

        obj = file[obj_name] if obj_name else file

        collector = self.get_metadata_collector(obj)
        record = Record(collector=collector, key_getter=self.record_key_getter)

        return record

    def gen_comparison_keys_common(self, keys):
        for key in keys:
            # in the default case, all three keys are the same
            # unlike in case of e.g. a->b renames that are explicitly given in input
            # this implements the semantics of "find items common to a and b using `key`"
            key_comp = key_a = key_b = key
            yield key_comp, key_a, key_b

    def gen_comparison_keys_subset(self, keys):
        for key_a, key_b in keys:
            key_comp = f'{key_a} -> {key_b}'
            yield key_comp, key_a, key_b

    def gen_comparison_pairs(self, a, b, subset=None):
        """
        Return an iterable of (key, comparison_pair), where comparison_pair is a tuple of (item_a, item_b) with a matching key.
        """
        # union of the keys of the two records
        # the ordering of the first record takes precedence
        # an alternative option would be to sort them, lexicographically or with a custom criteria
        keys_union = {**a, **b}.keys()

        if subset:
            keys_comp_a_b = self.gen_comparison_keys_subset(subset)
        else:
            keys_comp_a_b = self.gen_comparison_keys_common(keys_union)

        for key_comp, key_a, key_b in keys_comp_a_b:
            yield key_comp, (a.get(key_a, {}), b.get(key_b, {}))

    def get_comparison_metrics(self, *args, **kwargs):
        return ObjMetadataMetrics(*args, **kwargs)

    def compare(self, path_a, path_b, *args, obj_name=None, subset=None, **kwargs):
        # this assumes that the inputs are paths
        # otherwise, we can add some additional logic to detect the source type

        if obj_name is None or isinstance(obj_name, str):
            obj_names = [obj_name]
        else:
            obj_names = obj_name

        if len(obj_names) == 1:
            obj_names = obj_names * 2

        print(f'obj_names={obj_names}')

        file_a, file_b = [h5.File(path, 'r') for path in (path_a, path_b)]

        rec_a = self.get_record(file=file_a, obj_name=obj_names[0])
        rec_b = self.get_record(file=file_b, obj_name=obj_names[1])

        if subset is True:
            subset = [tuple(obj_names)]

        # print(f'rec_a={dict(rec_a)}')
        # print(f'rec_b={dict(rec_b)}')

        objs_metrics = []

        for key_comp, (obj_md_a, obj_md_b) in self.gen_comparison_pairs(rec_a, rec_b, subset=subset):

            # print(f'key_comp={key_comp}')
            obj_pair_metrics = self.get_comparison_metrics(key_comp, obj_md_a, obj_md_b)
            # print(f'obj_pair_a={obj_pair_metrics.a}')
            # print(f'obj_pair_b={obj_pair_metrics.b}')
            obj_pair_metrics.calculate()
            objs_metrics.append(obj_pair_metrics)


        self._metrics = self.get_metrics(objs_metrics)

        # are the files closed automatically where these variables are garbage-collected?
        file_a.close()
        file_b.close()
        return dict(self._metrics)

    def get_metrics(self, objs_metrics):
        """
        Get comparison metrics for the File pair from the metrics collected from the Object-level comparisons.
        """
        d = {}
        _S = DiffStatus

        for status in _S.iter():
            d[status] = [dict(obj_m) for obj_m in objs_metrics if obj_m['status'] == status]

        count_a_only = len(d.get(_S.deleted, []))
        count_b_only = len(d.get(_S.added, []))
        count_modified = len(d.get(_S.modified, []))
        count_unchanged = len(d.get(_S.unchanged, []))
        count_common = count_modified + count_unchanged

        count_a = count_common + count_a_only
        count_b = count_common + count_b_only

        d['count'] = {
            'a': count_a,
            'b': count_b,
            'a_only': count_a_only,
            'b_only': count_b_only,
            'modified': count_modified,
            'unchanged': count_unchanged,
        }

        d['summary'] = {
            _S.added: {
                'count': count_b_only,
                'relative_to': {
                    'a': count_b_only / count_a,
                    'b': count_b_only / count_b,
                }
            },
            _S.deleted: {
                'count': count_a_only,
                'relative_to': {
                    'a': count_a_only / count_a,
                    'b': count_a_only / count_b,
                },
            },
            _S.modified: {
                'count': count_modified,
                'relative_to': {
                    'a': count_modified / count_a,
                    'b': count_modified / count_b,
                }
            },
            _S.unchanged: {
                'count': count_unchanged,
                'relative_to': {
                    'a': count_unchanged / count_a,
                    'b': count_unchanged / count_b,
                }
            },
        }

        return d

    def percent_change(self):
        rel_frac = self._metrics['summary'][DiffStatus.modified]['relative_to']['a']
        return rel_frac * 100.

    def stats(self, changes):

        count = changes['count']
        print(f"compare A ({count['a']} Objects) with B ({count['b']} Objects)")

        section = changes['summary']
        for status, data in section.items():
            pct = data['relative_to']['a'] * 100.
            print(f"{status:<12}{data['count']:>8}\t{pct:>4.1f}%")
