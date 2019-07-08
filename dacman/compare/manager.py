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
        self._mpi_world = None

    def use_plugin(self, plugin):
        self.plugin = plugin

    @property
    def mpi_world(self):
        return self._mpi_world

    @mpi_world.setter
    def mpi_world(self, comm):
        self._mpi_world = comm

    def start(self):
        if self.executor == Executor.MPI:
            rank = self.mpi_world.Get_rank()
            if rank == 0:
                results = self.executor_map[self.executor].master(self.comparisons,
                                                                  self.mpi_world)
                self._print_results(results)
            else:
                self.executor_map[self.executor].workers(self.mpi_world, self.plugin)
        else:
            results = self.executor_map[self.executor].run(self.comparisons, self.plugin)
            self._print_results(results)

    def _print_results(self, results):
        if type(results) == list:
            for result in results:
                self._print(result)
        else:
            self._print(results)

    def _print(self, txt):
        if txt is not None:
            print(txt)
