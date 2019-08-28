import sys
try:
    import tigres
    TIGRES_IMPORT = True
except ImportError:
    TIGRES_IMPORT = False


import time
from dacman.compare.data import diff
import logging


def run(comparisons, plugin):
    if not TIGRES_IMPORT:
        print("tigres is not installed or possibly not in the path.")
        sys.exit()
    exec_name = 'EXECUTION_DISTRIBUTE_PROCESS'
    exec_plugin = tigres.utils.Execution.get(exec_name)
    diff_results = None
    logger = logging.getLogger(__name__)
    logger.info('Using tigres for parallel comparison.')

    try:
        logfile = 'dacman_diff_{}.log'.format(str(round(time.time())))
        tigres.start(name='dacman_diff', log_dest=logfile, execution=exec_plugin)
        tigres.set_log_level(tigres.Level.ERROR)

        task_array = tigres.TaskArray(tasks=[])
        input_array = tigres.InputArray(values=[])

        task_diff = tigres.Task("diff",
                                task_type=tigres.FUNCTION,
                                impl_name=diff)
        task_array.append(task_diff)

        # FIX THIS: how to pass keyword arg to tigres?
        for comparison in comparisons:
            input_array.append(tigres.InputValues(list_=comparison))

        diff_results = tigres.parallel('diff', input_array=input_array,
                                       task_array=task_array)

        logger = logging.getLogger(__name__)
        logger.info('Data comparison complete.')

    except tigres.utils.TigresException as e:
        print(str(e))
        logger.info('Error in comapring datasets using Tigres. {}'.format(e))
    finally:
        tigres.end()
        if diff_results is not None:
            return diff_results
