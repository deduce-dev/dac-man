from dacman.compare import base

import json
import logging
import os
import sys

_log = logging.getLogger(__name__)
_log.propagate = False
_pprint_formatter = logging.Formatter('%(message)s')
_std_formatter = logging.Formatter('[%(levelname)s] --- %(message)s')
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(_std_formatter)
_log.addHandler(_handler)


__author__ = 'You-Wei Cheah'
__email__ = 'ycheah@lbl.gov'


class JSONPlugin(base.Comparator):
    """Dac-Man plug-in to compare JSON files"""

    @staticmethod
    def description():
        return JSONPlugin.__doc__

    @staticmethod
    def supports():
        return ['json']

    pos_marker = '+=+'
    neg_marker = '-=-'

    def _does_basic_path_exists(self, paths: list) -> bool:
        result = True
        for path in paths:
            if not os.path.exists(path):
                _log.error(f'Invalid path: {path}')
                result = False
        return result

    def _pretty_print_diff(
            self, output: dict, prefix: str = '', indent: int = 2):
        space = indent * ' '
        for k, v in output.items():
            if k.startswith((self.pos_marker, self.neg_marker)):
                current_prefix, k = k[0], k[len(self.pos_marker):]
            else:
                current_prefix = prefix

            if type(v) is dict:
                _log.info(f'{current_prefix}{space}{k}: {{')
                new_indent = indent + 2
                self._pretty_print_diff(
                    v, prefix=current_prefix, indent=new_indent)
                _log.info(f'{current_prefix}{space}}}')
            else:
                _log.info(f'{current_prefix}{space}{k}: {v}')

    def _count_keys(self, data: json, level: int = 0) -> dict:
        key_counts = {level: 0}
        for k, v in data.items():
            if type(v) is dict:
                _key_counts = self._count_keys(v, level+1)
                for k, v in _key_counts.items():
                    key_counts[k] = v
            key_counts[level] += 1
        return key_counts

    def _collect_unique_key_stats(
            self, filename: str, data: dict, key_stats: dict):

        top_level = key_stats.setdefault(0, {})
        top_level[filename] = top_level.get(filename, 0) + 1

        if type(data) is not dict:
            return

        key_counts = self._count_keys(data)
        key_stats[f'n_{filename}_keys'] += (1 + sum(key_counts.values()))
        for level, count in key_counts.items():
            level_stats = key_stats.setdefault(level+1, {})
            level_stats[filename] = level_stats.get(filename, 0) + count

    def _compare_dict(
            self, a_data: json, b_data: json, level: int = 0) -> (dict, dict):
        """ Function to traverse the JSON data """
        return_val = {}

        a_key_set = set(a_data.keys())
        b_key_set = set(b_data.keys())
        key_stats = {
            f'n_{self.a_filename}_keys': 0,
            f'n_{self.b_filename}_keys': 0,
            'n_shared_keys': 0,
            level: {self.a_filename: 0, self.b_filename: 0, 'intersection': 0}}

        for k in a_key_set.difference(b_key_set):
            return_val[f'{self.pos_marker}{k}'] = a_data.get(k)
            self._collect_unique_key_stats(
                self.a_filename, a_data.get(k), key_stats)

        for k in b_key_set.difference(a_key_set):
            return_val[f'{self.neg_marker}{k}'] = b_data.get(k)
            self._collect_unique_key_stats(
                self.b_filename, b_data.get(k), key_stats)

        for k in a_key_set.intersection(b_key_set):
            key_stats['n_shared_keys'] += 1
            a_values = a_data.get(k)
            b_values = b_data.get(k)
            key_stats[level]['intersection'] += 1

            if all(type(v) is dict for v in (a_values, b_values)):
                output, _key_stats = self._compare_dict(
                    a_values, b_values, level+1)
                if output:
                    return_val[k] = output
                for k, v in _key_stats.items():
                    if type(v) is not dict:
                        key_stats[k] += v
                        continue
                    for file_type, count in v.items():
                        level_stats = key_stats.setdefault(level+1, {})
                        level_stats[file_type] = level_stats.get(
                            file_type, 0) + count

            elif a_values != b_values:
                return_val[f'{self.pos_marker}{k}'] = a_values
                return_val[f'{self.neg_marker}{k}'] = b_values

        return return_val, key_stats

    def compare(self, path_a: str, path_b: str, **kwargs):
        """ Core function for comparing JSON files """
        self.a_filename = os.path.basename(path_a)
        self.b_filename = os.path.basename(path_b)

        if not self._does_basic_path_exists((path_a, path_b)):
            return

        with open(path_a) as a_file, open(path_b) as b_file:
            a_data = json.load(a_file)
            b_data = json.load(b_file)

        diff_output, key_stats = self._compare_dict(a_data, b_data)
        if not diff_output:
            return
        self.key_stats = key_stats

        _handler.setFormatter(_pprint_formatter)
        disclaimer = (
            '\n'
            f'Contents in {self.a_filename} denoted with "+"\n'
            f'Contents in {self.b_filename} denoted with "-"\n'
            '\n'
        )

        _log.info(disclaimer)
        self._pretty_print_diff(diff_output)
        _handler.setFormatter(_std_formatter)

    def _gen_level0stats(self):
        comparison_text = 'more'
        if float(self._percent_change) < 0:
            comparison_text = 'less'

        level0_detail = (
            '\n'
            'Level 0 detail:\n'
            f'\t{self.a_filename} has {self._percent_change:04.2f}% '
            f'{comparison_text} keys than {self.b_filename}'
            '\n')
        return level0_detail

    def _gen_level1stats(self):
        n_shared_keys = self.key_stats.get('n_shared_keys')
        level1_detail = (
            '\n'
            'Level 1 detail:\n'
            f'\tTotal number of keys in {self.a_filename}: '
            f'{self.a_total_keys}\n'
            f'\tTotal number of keys in {self.b_filename}: '
            f'{self.b_total_keys}\n'
            '\tTotal number of overlapping keys in both files: '
            f'{n_shared_keys}'
            '\n')
        return level1_detail

    def _gen_level2stats(self):
        level2_details = []
        level2_header = '\nLevel 2 detail:'
        for json_level, details in self.key_stats.items():
            if not type(json_level) is int:
                # We have handled the aggregated stats in level 1
                continue

            level2_details.append(f'JSON level {json_level} has')
            for k, v in details.items():
                if k == 'intersection':
                    level2_details.append(
                        f'\t{v} keys shared between files')
                    continue
                level2_details.append((
                    f'\t{v} unique keys for {k}'))
        return f'{level2_header}\n\t' + '\n\t'.join(level2_details)

    def percent_change(self):
        try:
            self.a_total_keys = (
                self.key_stats.get(f'n_{self.a_filename}_keys')
                + self.key_stats.get('n_shared_keys'))
            self.b_total_keys = (
                self.key_stats.get(f'n_{self.b_filename}_keys')
                + self.key_stats.get('n_shared_keys'))
            diff = (self.a_total_keys - self.b_total_keys)
            self._percent_change = (diff / self.a_total_keys) * 100
        except Exception:
            return
        return self._percent_change

    def stats(self, changes, detail_level=2):
        if not self.percent_change():
            return

        outputs = []
        if detail_level >= 0:
            outputs.append(self._gen_level0stats())

        if detail_level >= 1:
            outputs.append(self._gen_level1stats())

        if detail_level >= 2:
            outputs.append(self._gen_level2stats())

        _handler.setFormatter(_pprint_formatter)
        for output in outputs:
            _log.info(output)
        _handler.setFormatter(_pprint_formatter)
