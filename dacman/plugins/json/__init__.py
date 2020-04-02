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


class JSONPlugin(base.Comparator):
    """Dac-Man plug-in to compare JSON files"""

    @staticmethod
    def description():
        return self.__doc__

    @staticmethod
    def supports():
        return ['json']

    pos_marker = '+=+'
    neg_marker = '-=-'

    def _does_basic_path_exists(self, paths):
        result = True
        for path in paths:
            if not os.path.exists(path):
                _log.error(f'Invalid path: {path}')
                result = False
        return result

    def compare(self, path_a: str, path_b: str, **kwargs):
        """ Core method for comparing json files """
        a_filename = os.path.basename(path_a)
        b_filename = os.path.basename(path_b)

        if not self._does_basic_path_exists((path_a, path_b)):
            return

        with open(path_a) as a_file, open(path_b) as b_file:
            a_data = json.load(a_file)
            b_data = json.load(b_file)

        diff_output = self._compare_dict(a_data, b_data)
        if not diff_output:
            return

        _handler.setFormatter(_pprint_formatter)
        disclaimer = (
            '\n'
            f'Contents in {a_filename} denoted with "+"\n'
            f'Contents in {b_filename} denoted with "-"\n'
            '\n'
        )
        _log.info(disclaimer)
        self._pretty_print_diff(diff_output)
        _handler.setFormatter(_std_formatter)

    def _pretty_print_diff(self, output: dict, prefix='', indent=2):
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

    def _compare_dict(self, a_data: json, b_data: json, level=0):
        return_val = {}

        a_key_set = set(a_data.keys())
        b_key_set = set(b_data.keys())

        for k in a_key_set.difference(b_data.keys()):
            return_val[f'{self.pos_marker}{k}'] = a_data.get(k)

        for k in b_key_set.difference(a_data.keys()):
            return_val[f'{self.neg_marker}{k}'] = b_data.get(k)

        for k in a_key_set.intersection(b_key_set):
            a_values= a_data.get(k)
            b_values = b_data.get(k)

            if type(a_values) is dict and type(b_values) is dict:
                need_output = self._compare_dict(a_values, b_values, level+1)
                if need_output:
                    return_val[k]= need_output

            elif a_values != b_values:
                return_val[f'{self.pos_marker}{k}'] = a_values
                return_val[f'{self.neg_marker}{k}'] = b_values

        return return_val

    def percent_change(self):
        return self._percent_change

    def stats(self, changes, detail_level=1):
        print(f'Stats: {changes}')
