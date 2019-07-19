import sys
import argparse
from pathlib import Path

from .util import to_json
from . import HDF5Plugin

comparator = HDF5Plugin()

parser = argparse.ArgumentParser(description=comparator.description())
parser.add_argument('files', metavar='A B', nargs=2, type=Path, help='Files to compare')
parser.add_argument('--objects', required=False, nargs='*', default=None)
parser.add_argument('-d', '--detail-level', required=False, type=int, default=1)

args = parser.parse_args()

comparator.compare(*args.files, obj_name=args.objects)

if args.detail_level >= 0:
    print(f'Percent change: {comparator.percent_change():.2f}%')
if args.detail_level >= 1:
    comparator.stats(comparator._metrics)
if args.detail_level >= 2:
    print(to_json(comparator._metrics))
