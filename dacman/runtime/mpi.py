from mpi4py import MPI
from dacman.compare.data import diff


def run(comparisons, plugin):
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
        change_pair_num = 0
        closed_workers = 0
        num_workers = size - 1

        print("Data changes in files:")
        while closed_workers < num_workers:
            result = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            source = status.Get_source()
            tag = status.Get_tag()

            if tag == States.READY:
                if change_pair_num < len(comparisons):
                    comm.send(comparisons[change_pair_num], dest=source, tag=States.START)
                    change_pair_num += 1
                else:
                    comm.send(None, dest=source, tag=States.EXIT)
            elif tag == States.DONE:
                pass
            elif tag == States.EXIT:
                closed_workers += 1

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
                diff(new_file, old_file, *args, comparator_plugin=plugin)
                comm.send(None, dest=0, tag=States.DONE)
            elif tag == States.EXIT:
                comm.send(None, dest=0, tag=States.EXIT)
                break
