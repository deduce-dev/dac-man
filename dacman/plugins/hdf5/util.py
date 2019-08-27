import json
import numpy as np


def extra_serializer(o):
    # TODO this should be applied for all numpy scalars
    if isinstance(o, np.int64):
        return int(o)
    if isinstance(o, bytes):
        # HDF5 text is read into Python as `bytes` objects
        # we decode them to strings when serializing to JSON
        # since JSON doesn't support raw bytes,
        # and the default serializer uses base64 encoder which is not human-readable
        return o.decode()
    else:
        # fallback case for complex datatypes?
        return repr(o)
    raise TypeError


def to_json(data):
    return json.dumps(data,
                      default=extra_serializer,
                      indent=4,
                      separators=(',', ': ')
                     )


def to_dict_basic_types(data):
    return json.loads(to_json(data))
