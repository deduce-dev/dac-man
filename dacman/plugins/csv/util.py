import json
import numpy


def to_serializeble(obj):
    if isinstance(obj, numpy.integer):
        return int(obj)
    elif isinstance(obj, numpy.floating):
        return float(obj)
    elif isinstance(obj, numpy.ndarray):
        return obj.tolist()
    else:
        return str(obj)


def to_json(data):
    return json.dumps(data, default=to_serializeble, indent=4)
