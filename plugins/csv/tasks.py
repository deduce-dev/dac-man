from pathlib import Path
import pandas as pd
import yaml

from invoke import task


# TODO change this name since it's a bit misleading
# "get_absolute_or_relative_to"
def _get_absolute(path, reference=None):
    path = Path(path)
    path_reference = Path(reference)

    return path if path.is_absolute() else path_reference.parent / path


# TODO this should be moved, either to its own module (if we decide we want to make it a first-class citizen)
# or, if not, at least to some `util` module
class Patch:
    
    @classmethod
    def from_path(cls, path):
        path = Path(path)
        return cls.from_yaml(Path(path).read_text(), path_base=path)
    
    @classmethod
    def from_yaml(cls, s, **kwargs):
        data = yaml.load(s)
        return cls(**data, **kwargs)
    
    def __init__(self, fields=None, values=None, _meta=None, path_base=None, **kwargs):
        self.fields = fields or {}
        self.values = values or []
        self._meta = _meta or {}
        
        self.path_base = path_base or None
        
    def apply_fields(self, df):
        return df.rename(columns=self.fields)
    
    def apply_values(self, df):
        df = df.copy()
        
        for update in self.values:
            (idx, col) = update['at']
            val = update['value']
            
            df.at[idx, col] = val
            
        return df
        
    def apply(self, df):
        
        funcs = [self.apply_fields, self.apply_values]
        
        for f in funcs:
            df = f(df)
            
        return df
    
    def run(self, source=None, target=None):

        assert source != target, "Source and target paths cannot be the same!"
        
        # TODO these should be configurable, although it's true that the patch internals/implementation
        # depend on these options to ensure the (almost) roundtripping
        def load(path):
            return pd.read_csv(path, dtype=str).fillna('')
        
        def save(df, path=None):
            return df.to_csv(path, index=False)

        print(f'loading dataframe from {source}')
        df_orig = load(source)
        print('applying changes')
        df_patched = self.apply(df_orig)
        print(f'saving patched dataframe to {target}')
        return save(df_patched, path=target)


@task(
    help={
        "patch": "Path to the patch spec file.",
        "source": ("Path to the file to which the patch should be applied."
                   "If not given, it will be taken from the patch. If relative, the same directory as `patch` will be assumed."),
        "target": "Path where the resulting patched version should be saved. The same criteria used for `source` apply.",
    },
    aliases=['patch'],
)
def apply_patch(c, patch, source=None, target=None):

    path_patch = Path(patch)
    patch = Patch.from_path(path_patch)

    source = Path(source or patch._meta['source'])
    target = Path(target or patch._meta['target'])

    source = _get_absolute(source, path_patch)
    target = _get_absolute(target, path_patch)

    patch.run(source, target)
