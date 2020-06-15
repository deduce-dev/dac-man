
from straight.plugin import load
from dacman.compare.base import Comparator
import dacman.core.utils as dacman_utils
import os
import logging
from functools import lru_cache


LOG = logging.getLogger(__name__)


class PluginManager(object):
    @classmethod
    def load_comparator(cls, data_type):
        COMPARATORS_MAP = get_comparators_map()
        plugin_config = os.path.join(os.getenv('HOME'), '.dacman/config/plugins.yaml')
        if os.path.exists(plugin_config):
            plugin_info = dacman_utils.load_yaml(plugin_config)
            LOG.debug(f'COMPARATORS_MAP={COMPARATORS_MAP}')
            if plugin_info is not None:
                if data_type in plugin_info:
                    # check if it's one of the default plugins for the data type
                    for comparator in COMPARATORS_MAP['default']:
                        if plugin_info[data_type] == comparator.__class__.__name__:
                            return comparator
                    # check if the data type plugin is available or not
                    if data_type in COMPARATORS_MAP:
                        for comparator in COMPARATORS_MAP[data_type]:
                            if comparator.__class__.__name__ == plugin_info[data_type]:
                                return comparator
                        else:
                            print(f"Configured plugin {plugin_info[data_type]} not found. Using available plugins.")
                    else:
                        print(f"Plugin for {data_type} not found. Using default plugin.")
        if data_type in COMPARATORS_MAP:
            return COMPARATORS_MAP[data_type][0]
        else:
            return COMPARATORS_MAP['default'][0]

    @classmethod
    def get_plugins(cls):
        plugins = load("dacman.plugins", subclasses=Comparator)
        plugin_list = []
        for plugin in plugins:
            plugin_list.append(plugin)
        return plugin_list


def _get_comparators():
    plugins = load("dacman.plugins", subclasses=Comparator)
    comparators = {}
    for plugin in plugins:
        comparator = plugin()
        LOG.debug(f'comparator={comparator}')
        supports = comparator.supports()
        LOG.info(f"Plugin {plugin} supports: {supports}")
        if type(supports) == list:
            for s in supports:
                _add_comparator(s, comparator, comparators)
        else:
            _add_comparator(supports, comparator, comparators)

    return comparators


def _add_comparator(supports, comparator, comparators):
    if supports in comparators:
        comparators[supports].append(comparator)
    else:
        comparators[supports] = [comparator]


# using a function instead of a global variable,
# so that the _get_comparators() function (and thus the leading of plug-ins)
# happens at runtime (i.e. only when Comparators are needed)
# rather than at import time (i.e. everytime `dacman` is invoked,
# even for actions that do not require Comparators)
# using lru_cache ensures that the _get_comparators() itself is only called once,
# since subsequent calls to get_comparators_map() will return the cached result:
# lru_cache uses a function's arguments as the cache key, and this function takes no arguments,
# so the "maxsize" argument has no effect and the cache size will always be 1
@lru_cache(maxsize=None)
def get_comparators_map():
    return _get_comparators()
