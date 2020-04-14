import sys
import argparse
from experiment import Experiment, AggregateMethod
from plot_classes.bar_plot import BarPlot
from plot_classes.box_plot import BoxPlot
import settings as _settings

def tput_redis_benchmark_bar_set_get(experiment_dir):
    # Figure 4
    pass


def tput_redis_benchmark_line_set(experiment_dir):
    # Figure 5 A
    pass


def tput_redis_benchmark_line_get(experiment_dir):
    # Figure 5 B
    pass


def tput_3_apps_local_live_buffered_w_1(experiment_dir):
    # Figure 6 A
    apps = ["als", "flux_msip", "flux_mscp"]
    data_sizes = ["10mb", "105b", "105b"]
    sources = [1, 2, 2]
    workers = [1]

    xtick_labels = ["Real-time", "Buffered"]

    apps_var_avg_values = []
    apps_var_std_values = []
    var = "normalized_throughput"
    std_var = "std_throughput"
    for i in range(len(apps)):
        exp_local_live = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=True, is_buffered=False)
        exp_local_buffered = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=True, is_buffered=True)

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_local_live.add_setup(sources[i], workers[j])
            exp_local_buffered.add_setup(sources[i], workers[j])

        exp_local_live.process()
        exp_local_buffered.process()

        apps_var_avg_values.append(exp_local_live.get_agg_results(var) +
            exp_local_buffered.get_agg_results(var))
        apps_var_std_values.append(exp_local_live.get_agg_results(std_var) + 
            exp_local_buffered.get_agg_results(std_var))

    bar_plot = BarPlot(plot_filename="tput_%s_local_live_buffered_w_1" % apps[i],
                       xlabel="Number of Workers",
                       ylabel="Throughput\n(tasks/s)")

    bar_plot.plot(
        apps_var_avg_values,
        xtick_labels,
        legends=["ImageAnalysis", "MovingAverage", "ChangeDetection"],
        std_arrs=apps_var_std_values)


def latency_3_apps_local_live_buffered_w_1(experiment_dir):
    # Figure 6 B
    apps = ["als", "flux_msip", "flux_mscp"]
    data_sizes = ["10mb", "105b", "105b"]
    sources = [1, 2, 2]
    workers = [1]

    xtick_labels = ["Real-time", "Buffered"]

    apps_var_avg_values = []
    apps_var_std_values = []
    var = "avg_event_time_latency"
    std_var = "std_event_time_latency"
    for i in range(len(apps)):
        exp_local_live = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=True, is_buffered=False)
        exp_local_buffered = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=True, is_buffered=True)

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_local_live.add_setup(sources[i], workers[j])
            exp_local_buffered.add_setup(sources[i], workers[j])

        exp_local_live.process()
        exp_local_buffered.process()

        apps_var_avg_values.append(exp_local_live.get_agg_results(var) +
            exp_local_buffered.get_agg_results(var))
        apps_var_std_values.append(exp_local_live.get_agg_results(std_var) + 
        exp_local_buffered.get_agg_results(std_var))

    bar_plot = BarPlot(plot_filename="latency_%s_local_live_buffered_w_1" % apps[i],
                       xlabel="Number of Workers",
                       ylabel="Latency (s)")

    bar_plot.plot(
        apps_var_avg_values,
        xtick_labels,
        legends=["ImageAnalysis", "MovingAverage", "ChangeDetection"],
        std_arrs=apps_var_std_values)


def tput_3_apps_2_modes_buffered_w_1_64(experiment_dir):
    # Figure 7 Throughput of apps with buffered data
    # comparing performance between local and cluster
    # modes from 1 to 64 workers
    apps = ["als", "flux_msip", "flux_mscp"]
    data_sizes = ["10mb", "105b", "105b"]
    sources = [1, 2, 2]
    workers = [1, 4, 8, 16, 32, 64]

    xtick_labels = [str(w) for w in workers]

    var = "normalized_throughput"
    for i in range(len(apps)):
        exp_local = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=True, is_buffered=True)
        exp_cori = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=False, is_buffered=True)

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_local.add_setup(sources[i], workers[j])
            exp_cori.add_setup(sources[i], workers[j])

        exp_local.process()
        exp_cori.process()

        box_plot = BoxPlot(plot_filename="tput_%s_2_modes_buffered_w_1_64" % apps[i],
                           xlabel="Number of Workers",
                           ylabel="Throughput\n(tasks/s)")

        box_plot.plot(
            [exp_local.get_agg_results(var),
            exp_cori.get_agg_results(var)],
            xtick_labels,
            legends=["ImageAnalysis", "MovingAverage", "ChangeDetection"]
        )


def tput_2_apps_2_modes_live_w_1_64(experiment_dir):
    # Figure 8 
    apps = ["flux_msip", "flux_mscp"]
    data_sizes = ["105b", "105b"]
    sources = [2, 2]
    workers = [1, 4, 8, 16, 32, 64]

    xtick_labels = [str(w) for w in workers]

    var = "all_throughput"
    for i in range(len(apps)):
        exp_local = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=True, is_buffered=False)
        exp_cori = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=False, is_buffered=False)

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_local.add_setup(sources[i], workers[j])
            exp_cori.add_setup(sources[i], workers[j])

        exp_local.process()
        exp_cori.process()

        apps_var_raw_values = [
            exp_local.get_agg_results(var, method=AggregateMethod.RAW),
            exp_cori.get_agg_results(var, method=AggregateMethod.RAW)
        ]

        box_plot = BoxPlot(plot_filename="tput_%s_2_modes_live_w_1_64" % apps[i],
                           xlabel="Number of Workers",
                           ylabel="Throughput\n(tasks/s)")

        box_plot.plot(
            apps_var_raw_values,
            xtick_labels,
            legends=["Local", "Remote"]
        )


def tput_3_apps_cori_buffered_w_64_640(experiment_dir):
    # Figure 9 
    apps = ["als", "flux_msip", "flux_mscp"]
    data_sizes = ["10mb", "105b", "105b"]
    sources = [1, 2, 2]
    workers = [64, 128, 256, 512, 640]

    xtick_labels = [str(w) for w in workers]

    var = "normalized_throughput"
    std_var = "std_throughput"
    for i in range(len(apps)):
        if apps[i] == "als":
            exp_cori = Experiment(apps[i], data_sizes[i], experiment_dir,
            is_local=False, is_buffered=True)
        else:
            exp_cori = Experiment(apps[i], data_sizes[i], experiment_dir,
            is_local=False, is_buffered=True, scaling_style="strong_scaling")

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_cori.add_setup(sources[i], workers[j])

        exp_cori.process()

        bar_plot = BarPlot(plot_filename="tput_%s_cori_buffered_w_64_640" % apps[i],
                           xlabel="Number of Workers",
                           ylabel="Throughput\n(tasks/s)")

        bar_plot.plot(
            [exp_cori.get_agg_results(var)],
            xtick_labels,
            std_arrs=[exp_cori.get_agg_results(std_var)])


def tput_1_app_cori_buffered_w_128_640_weak_scaling(experiment_dir):
    # Figure 10 A
    apps = ["flux_msip"]
    data_sizes = ["105b"]
    sources = [2, 4, 6, 8, 10]
    workers = [128, 256, 384, 512, 640]

    xtick_labels = [str(w) for w in workers]

    var = "normalized_throughput"
    for i in range(len(apps)):
        exp_cori = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=False, is_buffered=True, scaling_style="weak_scaling")

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_cori.add_setup(sources[j], workers[j])

        exp_cori.process()

        line_plot = LinePlot(plot_filename="tput_%s_cori_buffered_w_128_640_weak_scaling" % apps[i],
                           xlabel="Number of Workers",
                           ylabel="Throughput\n(tasks/s)")

        line_plot.plot(
            exp_cori.get_agg_results(var),
            xtick_labels,
            "--")


def tput_1_app_cori_buffered_w_64_throttling(experiment_dir):
    # Figure 10 B
    apps = ["als"]
    data_sizes = ["10mb"]
    sources = [1]
    workers = [64]

    #TODO read job count files
    pass


def tput_1_app_cori_live_w_640_payload_2_10_mb(experiment_dir):
    # Figure 11
    apps = ["als"]
    data_sizes = ["2mb", "4mb", "6mb", "8mb", "10mb"]
    sources = [1]
    workers = [640]

    xtick_labels = data_sizes

    apps_var_raw_values = []
    var = "all_throughput"
    for i in range(len(data_sizes)):
        exp_cori = Experiment(apps[0], data_sizes[i], experiment_dir,
        is_local=False, is_buffered=False)

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_cori.add_setup(sources[j], workers[j])

        exp_cori.process()

        res = exp_cori.get_agg_results(var, AggregateMethod.RAW)
        apps_var_raw_values.append(res[0])

    #print(len(apps_var_raw_values[0]))

    box_plot = BoxPlot(plot_filename="tput_%s_cori_live_w_640_payload_2_10_mb" % apps[0],
                       xlabel="Data-sizes (MB)",
                       ylabel="Throughput\n(tasks/s)")
                       #, ylim_top=20)

    box_plot.plot(
        [apps_var_raw_values],
        xtick_labels
    )


def latency_1_app_cori_live_w_640_payload_2_10_mb(experiment_dir):
    # Figure 12
    apps = ["als"]
    data_sizes = ["2mb", "4mb", "6mb", "8mb", "10mb"]
    sources = [1]
    workers = [640]

    xtick_labels = data_sizes

    apps_var_raw_values = []
    var = "all_event_time_latency"
    for i in range(len(data_sizes)):
        exp_cori = Experiment(apps[0], data_sizes[i], experiment_dir,
        is_local=False, is_buffered=False)

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_cori.add_setup(sources[j], workers[j])

        exp_cori.process()

        res = exp_cori.get_agg_results(var, AggregateMethod.RAW)
        apps_var_raw_values.append(res[0])

        box_plot = BoxPlot(plot_filename="latency_%s_cori_live_w_640_payload_2_10_mb" % apps[0],
                           xlabel="Data-sizes (MB)",
                           ylabel="Latency (s)")

    box_plot.plot(
        [apps_var_raw_values],
        xtick_labels
    )


def tput_2_apps_cori_live_w_64_pipeline_vs_non_pipeline(experiment_dir):
    # Figure 13
    apps = ["als", "flux_msip"]
    data_sizes = ["10mb", "105b"]
    sources = [1, 2]
    workers = [64]

    xtick_labels = ["ImageAnalysis", "MovingAverage"]

    var = "normalized_throughput"
    std_var = "std_throughput"
    pass


# example
def tput_1_app_cori_live_w_1_64(experiment_dir):
    # example
    apps = ["flux_msip"]
    data_sizes = ["105b"]
    sources = [2]
    workers = [1, 4, 8, 16, 32, 64]

    xtick_labels = [str(w) for w in workers]

    var = "normalized_throughput"
    std_var = "std_throughput"
    for i in range(len(apps)):
        exp_cori = Experiment(apps[i], data_sizes[i], experiment_dir,
        is_local=False, is_buffered=False)

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_cori.add_setup(sources[i], workers[j])

        exp_cori.process()

        bar_plot = BarPlot(plot_filename="tput_%s_cori_buffered_w_64_640" % apps[i],
                           xlabel="Number of Workers",
                           ylabel="Throughput\n(tasks/s)")

        bar_plot.plot(
            [exp_cori.get_agg_results(var)],
            xtick_labels,
            legends=["ALS"],
            std_arrs=exp_cori.get_agg_results(std_var))


def main(args):
    experiment_dir = args.experiment_dir
    figure_num = args.figure_num

    #tput_1_app_cori_live_w_1_64(experiment_dir)

    if figure_num == 0:
        tput_redis_benchmark_bar_set_get(experiment_dir)
        tput_redis_benchmark_line_set(experiment_dir)
        tput_redis_benchmark_line_get(experiment_dir)
        tput_3_apps_local_live_buffered_w_1(experiment_dir)
        latency_3_apps_local_live_buffered_w_1(experiment_dir)
        #tput_3_apps_2_modes_buffered_w_1_64(experiment_dir)
        tput_2_apps_2_modes_live_w_1_64(experiment_dir)
        exit()
        tput_3_apps_cori_buffered_w_64_640(experiment_dir)
        tput_1_app_cori_buffered_w_128_640_weak_scaling(experiment_dir)
        tput_1_app_cori_buffered_w_64_throttling(experiment_dir)
        tput_1_app_cori_live_w_640_payload_2_10_mb(experiment_dir)
        latency_1_app_cori_live_w_640_payload_2_10_mb(experiment_dir)
    elif figure_num == 4:
        tput_redis_benchmark_bar_set_get(experiment_dir)
    elif figure_num == 5:
        tput_redis_benchmark_line_set(experiment_dir)
        tput_redis_benchmark_line_get(experiment_dir)
    elif figure_num == 6:
        tput_3_apps_local_live_buffered_w_1(experiment_dir)
        latency_3_apps_local_live_buffered_w_1(experiment_dir)
    elif figure_num == 7:
        #tput_3_apps_2_modes_buffered_w_1_64(experiment_dir)
        pass
    elif figure_num == 8:
        tput_2_apps_2_modes_live_w_1_64(experiment_dir)
    elif figure_num == 9:
        tput_3_apps_cori_buffered_w_64_640(experiment_dir)
    elif figure_num == 10:
        tput_1_app_cori_buffered_w_128_640_weak_scaling(experiment_dir)
        tput_1_app_cori_buffered_w_64_throttling(experiment_dir)
    elif figure_num == 11:
        tput_1_app_cori_live_w_640_payload_2_10_mb(experiment_dir)
    elif figure_num == 12:
        latency_1_app_cori_live_w_640_payload_2_10_mb(experiment_dir)
    elif figure_num == 13:
        tput_2_apps_cori_live_w_64_pipeline_vs_non_pipeline(experiment_dir)
    elif figure_num < 4:
        raise ValueError("Figure %d cannot be generated" % figure_num)
    else:
        raise ValueError("Figure %d doesn't exist" % figure_num)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-e', '--experiment_dir', type=str, required=False,
        default=_settings.EXPERIMENT_DIR,
        help='Path to all experiments'
    )

    parser.add_argument(
        '-f', '--figure_num', type=int, required=False, default=0,
        help='Choose figure-num (from paper) to display. Default is 0 -- all figures'
    )

    args = parser.parse_args()

    main(args)