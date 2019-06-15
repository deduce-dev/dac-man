

class Diff:
    """
    The result of a diff operation.

    Some ideas for the interface:
    - Fundamental units/kinds/... (added, deleted, changed, unchanged)
    - Context: information about parameters/options/conditions that affect how the diff is computed

    Other aspects:
    - Serialization: export to record, i.e. dict with base types only (so that it can be exported losslessly to JSON/YAML)
    - Deserialization: recreate losslessly from record
        - This is important if we want to:
            - Use DiffView objects as a base for visualization
            - Use Diff objects as the unified interface, i.e. view = DiffView(diff)
            - Be able to create DiffView objects from serialized Diff objects (i.e. "offline", after the diff was computed)
    """
    # TODO this should rather be component_serializer or something
    # converter = list
    converter_record = list
    converter_display = None

    def __init__(self,
                 added=None, deleted=None, changed=None, unchanged=None,
                 context=None,
                 # TODO maybe this could be included in the context, or in a "metrics" dict, so as to relax the interface a bit
                 data_info=None,
                 factory=list,
                 **kwargs,
    ):
        # TODO this is a bit tedious. Consider wrapping in a class?
        self.added = added if added is not None else factory()
        self.deleted = deleted if deleted is not None else factory()
        self.changed = changed if changed is not None else factory()
        self.unchanged = unchanged if unchanged is not None else factory()

        self.context = context or {}
        # or maybe "context" can be a kitchen sink and include also kwargs?
        self.context.update(**kwargs)

        # TODO is there a reasonable default?
        self.data_info = data_info or {}

        # TODO what's needed to do the analysis?
        # - len(data_old)
        # - len(data_new)
    def to_record(self, converter=None):
        # TODO this probably belongs in the base class,
        # but we have to figure out a smart way for subclasses to extend it

        converter = converter or self.converter_record
        # slightly involved, but in this way we keep the functional flow
        if converter is None:
            converter = lambda x: x

        # TODO to_record values should only contain basic types: decide which ones
        # TODO my guess is that these will generally be lists/arrays. Is it always true?
        d = {
            'added': converter(self.added),
            'deleted': converter(self.deleted),
            'unchanged': converter(self.unchanged),
            'changed': converter(self.changed),
            # '_context': self.context,
        }

        return self.with_context(d)
    
    def with_context(self, d):
        # TODO this should be immutable. But then we have to deepcopy?
        d['_context'] = self.context
        return d

    def __repr__(self):
        return f'<{type(self).__name__}>'

    def display(self):
        from IPython.display import display, display_markdown
        display(str(self))

        display_markdown('added', raw=True)
        display(self.added)
        display_markdown('deleted', raw=True)
        display(self.deleted)
        display_markdown('unchanged', raw=True)
        display(self.unchanged)
        display_markdown('changed', raw=True)
        display(self.changed)

    # to use in Jupyter Notebooks
    def _ipython_display_(self):
        return self.display()


class Differ:
    """
    Implements the general interface f(pre, post) -> Diff

    Any callable matching this signature can be a Differ: this base class is mainly used to store steering parameters (at object instantiation)
    (a similar result can be obtained with currying, e.g. functools.partial).

    One essential property of Differ objects is that they must be stateless with respect to the (pre, post) data, i.e. the same differ instance
    is used to process all (appropriate) change pairs in the changeset.
    """
    diff_factory = Diff

    def get_diff(self, pre, post):
        return self.diff_factory(pre, post)

    def __call__(self, *args):
        return self.get_diff(*args)


class DiffBuilder:
    """
    I'm not really sure whether this is strictly needed.
    
    The idea is that, in general, we don't want to store the (pre, post) data in the Diff object, in case we want to accumulate them directly.
    However, in some cases, it can be beneficial to store that state in an object while processing the diff (i.e. creating and filling the Diff object),
    which is then discarded (generally, automatically, at te end of differ(pre, post)).

    This class would then be used as an intermediate step in the chain:
    Differ -> DiffBuilder -> Diff

    One alternative would be to have a "heavy" Diff object (holding on the (pre, post) data),
    and let the caller (that in any case is responsible for the accumulation) decide whether to store it directly, or only a view of it:

    Differ -> Diff -> DiffReport/Diff.to_record()
    """


class DiffDataClientMixin:
    """
    Convenience mixin class for classes (typically, but not necessarily, DiffBuilders) mantaining bindings to the diff data.
    """

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data_pair):
        assert len(data_pair) == 2
        self._data = data_pair

    def __iter__(self):
        return iter(self.data)

    @property
    def old(self):
        return self.data[0]

    @property
    def new(self):
        return self.data[1]


class DiffClient:

    def __init__(self, diff=None, **kwargs):
        self.diff = diff
