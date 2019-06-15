from argparse import ArgumentParser
from pathlib import Path

from . import TableDiffer
from .viewers import PrettyPrint


def get_cli_parser():
    """
    Create and setup the parser to process the CLI arguments.
    """
    parser = ArgumentParser()
    # using the `type` kwarg is used to automatically validate the parsed value at the CLI invocation stage
    # invalid values result in an immediate Argparse exception (i.e. the same as providing invalid flags)
    parser.add_argument('old', type=Path, help='path to old file')
    parser.add_argument('new', type=Path, help='path to new file')
    parser.add_argument('-f', '--format', type=str, required=False, choices=['json'], default='json', help='output format of the diff')
    parser.add_argument('-c', '--config', required=False, default=None, help='path to configuration file')

    return parser


def main():
    parser = get_cli_parser()
    args = parser.parse_args()

    old, new = args.old, args.new
    format_ = args.format

    config = args.config

    if config:
        differ = TableDiffer.from_config_py(Path(config))
    else:
        differ = TableDiffer()

    diff = differ(old, new)
    diff_record = diff.to_record()

    if format_ == 'json':

        output_str = str(PrettyPrint(diff))

        print(output_str)
