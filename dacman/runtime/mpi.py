import sys
try:
    from mpi4py import MPI
    MPI4PY_IMPORT = True
except ImportError:
    MPI4PY_IMPORT = False
from dacman.compare.data import diff

import logging


def run(comparisons, plugin):
    if not MPI4PY_IMPORT:
        print("mpi4py is not installed or possibly not in the path.")
        sys.exit()
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    status = MPI.Status()

    class States():
        READY = 0
        START = 1
        DONE = 2
        EXIT = 3

    if rank == 0:
        logger = logging.getLogger(__name__)
        logger.info('Using MPI for parallel comparison.')

        change_pair_num = 0
        closed_workers = 0
        num_workers = size - 1
        results = []

        print("Data changes in files:")
        while closed_workers < num_workers:
            result = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            source = status.Get_source()
            tag = status.Get_tag()

            if tag == States.READY:
                if change_pair_num < len(comparisons):
                    print(comparisons[change_pair_num])
                    comm.send(comparisons[change_pair_num], dest=source, tag=States.START)
                    change_pair_num += 1
                else:
                    comm.send(None, dest=source, tag=States.EXIT)
            elif tag == States.DONE:
                results.append(result)
            elif tag == States.EXIT:
                closed_workers += 1

        logger.info('Data comparison complete.')
        return results
    else:
        # only start parallel processing if data change is required
        while True:
            comm.send(None, dest=0, tag=States.READY)
            comparison = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()

            if tag == States.START:
                new_file = comparison[0]
                old_file = comparison[1]
                args = []
                if len(comparison) > 2:
                    for arg in comparison[2:]:
                        args.append(arg)
                result = diff(new_file, old_file, *args, comparator_plugin=plugin)
                comm.send(result, dest=0, tag=States.DONE)
            elif tag == States.EXIT:
                comm.send(None, dest=0, tag=States.EXIT)
                break
