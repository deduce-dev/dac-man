
from straight.plugin import load
from dacman.compare.base import ComparatorBase


class PluginManager(object):
    @classmethod
    def load_comparator(cls, data_type):
        if data_type in COMPARATORS_MAP:
            return COMPARATORS_MAP[data_type]
        else:
            return COMPARATORS_MAP['default']


def get_comparators():
    plugins = load("dacman.plugins", subclasses=ComparatorBase)
    comparators = {}
    for plugin in plugins:
        comparator = plugin()
        supports = comparator.supports()
        #print("Plugin {} supports: {}".format(plugin.__name__, supports))
        if type(supports) == list:
            for s in supports:
                if s in comparators:
                    comparators[s].append(comparator)
                else:
                    comparators[s] = comparator
        else:
            if supports in comparators:
                comparators[supports].append(comparator)
            else:
                comparators[supports] = comparator

    return comparators


COMPARATORS_MAP = get_comparators()
