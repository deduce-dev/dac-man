
from straight.plugin import load
from dacman.compare.base import ComparatorBase


class PluginManager(object):
    @classmethod
    def load_comparator(cls, data_type):
        if data_type in COMPARATORS_MAP:
            return COMPARATORS_MAP[data_type]
        else:
            return COMPARATORS_MAP['default']

    @classmethod
    def get_plugins(cls):
        plugins = load("dacman.plugins", subclasses=ComparatorBase)
        plugin_list = []
        for plugin in plugins:
            plugin_list.append(plugin)
        return plugin_list


def get_comparators():
    plugins = load("dacman.plugins", subclasses=ComparatorBase)
    comparators = {}
    for plugin in plugins:
        comparator = plugin()
        supports = comparator.supports()
        # print("Plugin {} supports: {}".format(plugin.__name__, supports))
        # For different plugins for the same datatype, a plugin will
        # be selected at random. Fix later...
        if type(supports) == list:
            for s in supports:
                comparators[s] = comparator
        else:
            comparators[supports] = comparator

    return comparators


COMPARATORS_MAP = get_comparators()
