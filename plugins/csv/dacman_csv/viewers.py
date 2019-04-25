import json

from . import _base


# TODO maybe at some point it will make sense to have a lightweight DiffData class
def display_diff_data(old, new):
    from IPython.display import display, display_pretty

    print('displaying diff data:')
    print('old:')
    display(old)
    print('new:')
    display(new)


class _ExtendedJSONEncoder(json.JSONEncoder):

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


class PrettyPrint(_base.DiffClient):
    
    def __init__(self, diff=None, backend='json', **kwargs):
        self.diff = diff
        self.backend = backend

    def render(self):
        if self.backend == 'json':
            return json.dumps(self.diff.to_record(), indent=4, separators=(', ', ': '), cls=_ExtendedJSONEncoder)

    def __repr__(self):
        return self.render()


class Interactive(_base.DiffClient):

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