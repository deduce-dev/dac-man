#!/usr/bin/env python


import pandas as pd

from enum import Enum
import numpy as np


from pathlib import Path
from argparse import ArgumentParser
import json



class BaseDiffViewer:
    
    def __init__(self, diff=None, **kwargs):
        self.diff = diff


class ExtendedJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        import os

        if isinstance(obj, os.PathLike):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        # this should cover most of our needs regarding functions
        if callable(obj):
            return str(obj)

        return super().default(obj)


class PrettyPrint(BaseDiffViewer):
    
    def __init__(self, diff=None, backend='json', **kwargs):
        self.diff = diff
        self.backend = backend

    def render(self):
        if self.backend == 'json':
            return json.dumps(self.diff.to_record(), indent=4, separators=(', ', ': '), cls=ExtendedJSONEncoder)

    def __repr__(self):
        return self.render()


class Interactive(BaseDiffViewer):

    @property
    def stack(self):
        return self.diff.values._stack

    def apply_status_color(self, df):
    
        status = self.stack['status'].loc[df.index, df.columns]
    
        status_prop_map = {
            # TODO rethink color palette, especially in terms of accessibility
            'C': 'background-color: #ffff99',
            'D': 'background-color: #ffad99',
            'A': 'background-color: #99ff99',
            'N': 'background-color: #cccccc',
            'U': '',
        }

        return status.apply(lambda c: c.map(status_prop_map), axis=0)

    def get_style(self, df):
        return (df
                .dropna(axis='index', how='all')
                .style
                .apply(self.apply_status_color, axis=None)
                )

    def get_stack_style(self):
        return {field: self.get_style(df)
                for field, df in self.stack.items()}

    def get_view_selector(self):
        from ipywidgets import widgets
        return widgets.ToggleButtons(
            options=['old', 'new', 'difference', 'status'],
            description='View: ',
            disabled=False,
            button_style='', 
        )

    def get_sort_selector(self):
        from ipywidgets import widgets

        return widgets.Dropdown(
            options=self.diff.schema.unchanged,
            value=None,
            description='Sort by: ',
        )

    def _ipython_display_(self):
        from IPython.display import display

        display(self.display())

    def display(self):
        from IPython.display import display
        from ipywidgets import widgets

        def f(sort_by=None, key=None):
            # df = self.get_stack_style()[]
            df = (self.stack[key]
                  .dropna(axis='index', how='all')
            )
            if sort_by:
                df = df.sort_values(sort_by)

            df.drop
            display(df.pipe(self.get_style))

        interactive_output = widgets.interactive(f, 
            sort_by=self.get_sort_selector(),
            key=self.get_view_selector(),
        )

        output = interactive_output.children[-1]
        output.layout.height = '700px'
        return interactive_output


# TODO maybe at some point it will make sense to have a lightweight DiffData class
def display_diff_data(old, new):
    from IPython.display import display, display_pretty

    print('displaying diff data:')
    print('old:')
    display(old)
    print('new:')
    display(new)


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
        # TODO move this to appropriate DiffView class
        output = json.dumps(diff_record, indent=4, separators=(', ', ': '))
        print(output)

if __name__ == "__main__":
    main()