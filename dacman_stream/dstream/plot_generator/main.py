import sys
import argparse
from plot_classes import BoxPlot, BarPlot
from experiment import Experiment, AggregateMethod

def tput_2_apps_2_modes_live_w_1_64(experiment_dir):
    # Figure 8 Throughput of apps with buffered data
    # comparing performance between local and cluster
    # modes from 1 to 64 workers
    apps = ["flux_msip", "flux_mscp"]
    data_sizes = ["105b", "105b"]
    sources = [2, 2]
    workers = [1, 4, 8, 16, 32, 64]

    var = "normalized_throughput"
    for i in range(len(apps)):
        exp_local = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=True, is_buffered=False)
        exp_cori = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=False, is_buffered=False)

        for j in range(workers):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_local.add_setup(sources[i], workers[j])
            exp_cori.add_setup(sources[i], workers[j])

        exp_local.process()
        exp_cori.process()

        box_plot = BoxPlot(xticks_labels=[str(w) for w in workers],
                           plot_filename="tput_%s_2_modes_live_w_1_64" % app,
                           xlabel="Number of Workers",
                           ylabel="Throughput\n(tasks/s)")

        box_plot.plot(
            exp_local.get_agg_results(var),
            exp_cori.get_agg_results(var)
        )


def tput_3_apps_2_modes_buffered_w_1_64(experiment_dir):
    # Figure 8 Throughput of apps with buffered data
    # comparing performance between local and cluster
    # modes from 1 to 64 workers
    apps = ["als", "flux_msip", "flux_mscp"]
    data_sizes = ["10mb", "105b", "105b"]
    sources = [1, 2, 2]
    workers = [1, 4, 8, 16, 32, 64]

    var = "normalized_throughput"
    for i in range(len(apps)):
        exp_local = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=True, is_buffered=True)
        exp_cori = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=False, is_buffered=True)

        for j in range(workers):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_local.add_setup(sources[i], workers[j])
            exp_cori.add_setup(sources[i], workers[j])

        exp_local.process()
        exp_cori.process()

        box_plot = BoxPlot(xticks_labels=[str(w) for w in workers],
                           plot_filename="tput_%s_2_modes_buffered_w_1_64" % app,
                           xlabel="Number of Workers",
                           ylabel="Throughput\n(tasks/s)")

        box_plot.plot(
            exp_local.get_agg_results(var),
            exp_cori.get_agg_results(var)
        )



def main():
    experiment_dir = sys.argv[1]
    tput_3_apps_2_modes_buffered_w_1_64(experiment_dir)


if __name__ == '__main__':
    main()