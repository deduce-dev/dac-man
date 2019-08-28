
from straight.plugin import load
from dacman.compare.base import Comparator
import dacman.core.utils as dacman_utils
import os
import logging


LOG = logging.getLogger(__name__)


class PluginManager(object):
    @classmethod
    def load_comparator(cls, data_type):
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
                            print("Configured plugin {} not found. Using available plugins.".format(plugin_info[data_type]))
                    else:
                        print("Plugin for {} not found. Using default plugin.".format(data_type))
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
    plugins = load("dacman.plugins", subclasses=Comparator, recurse=True)
    comparators = {}
    for plugin in plugins:
        comparator = plugin()
        LOG.debug(f'comparator={comparator}')
        supports = comparator.supports()
        LOG.info("Plugin {} supports: {}".format(plugin, supports))
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


COMPARATORS_MAP = _get_comparators()
