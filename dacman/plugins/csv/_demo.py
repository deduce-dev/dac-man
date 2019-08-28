"""
Utility classes and functions used to prepare documentation, examples, and other additional material.
"""

from pathlib import Path
from contextlib import contextmanager
from textwrap import dedent

from . import CSVPlugin
from .util import to_json

from IPython.display import display


@contextmanager
def codeblock(language='txt', lines=None):
    # print(f'```{language} hl_lines=""')
    print(f'\n```{language}')
    yield None
    print('```\n')


class DemoCSVSource:
    @classmethod
    def display_all(cls, *sources):
        for src in sources:
            display(src)

    def __init__(self, key, text):
        self.key = key
        self.text = dedent(text).strip('\n')

        self.path.write_text(self.text)

    @property
    def path(self):
        return Path('/tmp') / f'{self.key}.csv'
    
    def _ipython_display_(self):

        with codeblock('csv'):
            print(self.text)
            
    def display_with(self, other):
        self.display_all(self, other)


def display_dict(data, keys=None):
    keys = keys or data.keys()
    subset = {k: v for (k, v) in data.items() if k in keys}

    with codeblock('json'):
        print(to_json(subset))


def to_dtypes_frame(df):
    return (pd.DataFrame(df.dtypes, columns=['dtype'])
            .rename_axis('colname', axis='index')
            .loc[lambda d: ~d.index.isin(['__lineno', '__grididx'])]
           )


class DemoCSVPlugin(CSVPlugin):
    def __init__(self, a, b, **kwargs):
        super().__init__()
        self._opts = kwargs
        
        self._metrics = self.compare(a.path, b.path)

    @property
    def calc_options(self):
        return dict(self._opts)
    
    def display_opts(self, **kwargs):
        display_dict(self._opts, **kwargs)
            
    def display_metrics(self, **kwargs):
        display_dict(self._metrics, **kwargs)

    def display_stats(self):
        with codeblock():
            self.stats(self._metrics)