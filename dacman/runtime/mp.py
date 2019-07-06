
import multiprocessing
from dacman.compare.data import diff


def run(comparisons, plugin):
    num_procs = multiprocessing.cpu_count()
    results = []
    pool = multiprocessing.Pool(processes=num_procs)
    for comparison in comparisons:
        print(comparison)
        args = tuple(comparison)
        result = pool.apply_async(diff, args=args,
                                  kwds={'comparator_plugin': plugin})
        results.append(result)

    pool.close()
    pool.join()
