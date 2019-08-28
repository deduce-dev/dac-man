'''
Python multiprocessing executor
'''

import multiprocessing
from dacman.compare.data import diff
import logging


def run(comparisons, plugin):
    logger = logging.getLogger(__name__)
    num_procs = multiprocessing.cpu_count()
    logger.info('Using Python multiprocessing for parallel comparison.')
    results = []
    pool = multiprocessing.Pool(processes=num_procs)
    for comparison in comparisons:
        #print(comparison)
        args = tuple(comparison)
        result = pool.apply_async(diff, args=args,
                                  kwds={'comparator_plugin': plugin})
        results.append(result.get())

    pool.close()
    pool.join()

    logger.info('Data comparison complete.')
    return results
