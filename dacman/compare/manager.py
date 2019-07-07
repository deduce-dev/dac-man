from dacman.runtime import st, mp, mpi, tigres
from dacman.runtime import Executor


class DataDiffer(object):
    def __init__(self, comparisons, executor=Executor.DEFAULT):
        self.executor_map = {Executor.DEFAULT: st,
                             Executor.THREADED: mp,
                             Executor.MPI: mpi,
                             Executor.TIGRES: tigres}
        self.comparisons = comparisons
        self.plugin = None
        self.executor = executor

    def use_plugin(self, plugin):
        self.plugin = plugin

    def start(self):
        print("Runtime = {}".format(self.executor))
        self.executor_map[self.executor].run(self.comparisons, self.plugin)
