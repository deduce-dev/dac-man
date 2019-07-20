import sys
import argparse
from pathlib import Path

from .util import to_json
from . import HDF5Plugin

plugin = HDF5Plugin()

parser = argparse.ArgumentParser(prog='python -m dacman.plugins.hdf5', description=plugin.description())
parser.add_argument('path_a', metavar='A', type=Path, help='Path to first HDF5 file to compare.')
parser.add_argument('path_b', metavar='B', type=Path, help='Path to second HDF5 file to compare.')
parser.add_argument('--objects',
                    required=False,
                    nargs='*',
                    default=None,
                    help="""
                    Object name(s) to compare within files A and B.
                    Can be either a single value `name`, or a pair of values `name_a name_b`.
                    If `name`, the comparison will be between A[name] and B[name].
                    If `name_a name_b`, the comparison will be between A[name_a] and B[name_b].
                    If not given (the default), the comparison will be between A and B.
                    """
                    )
parser.add_argument('-d', '--detail-level', required=False,
                    type=int,
                    default=1,
                    help="""
                    Level of detail of the change information given in output (larger values: more detail).
                     0: Display overall amount of change as a single number.
                     1: Display aggregated change statistics (the default).
                    2+: Display properties and change metrics for each Object.
                    """
                    )

args = parser.parse_args()

plugin.compare(args.path_a, args.path_b, obj_name=args.objects)

if args.detail_level >= 0:
    print(f'Percent change: {plugin.percent_change():.2f}%')
if args.detail_level >= 1:
    plugin.stats(plugin._metrics)
if args.detail_level >= 2:
    print(to_json(plugin._metrics))
