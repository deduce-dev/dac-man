'''
A single-threaded executor
'''

from dacman.compare.data import diff
import logging


def run(comparisons, plugin):
    logger = logging.getLogger(__name__)
    logger.info('Sequentially comparing dataset pairs.')
    results = []
    for comparison in comparisons:
        #print(comparison)
        argv = []
        if len(comparison) > 2:
            argv = comparison[2:]
        result = diff(comparison[0], comparison[1], *argv, comparator_plugin=plugin)
        results.append(result)
    logger.info('Data comparison complete.')
    return results
