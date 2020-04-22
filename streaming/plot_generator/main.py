import os
import sys
import argparse
import csv
import numpy as np
from experiment import Experiment, AggregateMethod
from redis_stat_generator import RedisStatGenerator
from plot_classes.line_plot import LinePlot
from plot_classes.bar_plot import BarPlot
from plot_classes.box_plot import BoxPlot
import settings as _settings


def tput_redis_benchmark_bar_set_get(experiment_dir):
    # Figure 4
    client_num = [64]
    data_sizes = ['1 KB', '50 KB', '100 KB', '1 MB', '10 MB']

    redis_stat_gen = RedisStatGenerator()

    avg_clients_cmds, std_clients_cmds, all_xtick_labels = redis_stat_gen.compare_clients_num(
        os.path.join(
            experiment_dir,
            "redis_benchmark_results",
            "n_1000"
        )
    )

    client_num_str = "c_%d" % client_num[0]

    clients_avg_set_vals = []
    clients_avg_get_vals = []
    clients_std_set_vals = []
    clients_std_get_vals = []
    for i in range(len(avg_clients_cmds)):
        avg_cli_num, avg_cli_dict = avg_clients_cmds[i]
        std_cli_num, std_cli_dict = std_clients_cmds[i]
        if avg_cli_num != client_num_str:
            continue

        cli_avg_set_val_list = []
        cli_avg_get_val_list = []
        cli_std_set_val_list = []
        cli_std_get_val_list = []
        for j, v in enumerate(all_xtick_labels):
            if v in data_sizes:
                cli_avg_set_val_list.append(avg_cli_dict['SET'][j])
                cli_avg_get_val_list.append(avg_cli_dict['GET'][j])
                cli_std_set_val_list.append(std_cli_dict['SET'][j])
                cli_std_get_val_list.append(std_cli_dict['GET'][j])
        clients_avg_set_vals.append(cli_avg_set_val_list)
        clients_avg_get_vals.append(cli_avg_get_val_list)
        clients_std_set_vals.append(cli_std_set_val_list)
        clients_std_get_vals.append(cli_std_get_val_list)
    
    bar_plot = BarPlot(plot_filename="redis_benchmark_tput_bar_c_64_datasize_set_get",
                       xlabel="Data-sizes (KB)",
                       ylabel="Throughput\n(requests/s)",
                       inner_txt_rotation="vertical", inner_txt_size=20,
                       fig_size1=12, fig_size2=8, width=0.45, legend_size=25,
                       legend_loc="best", ylim_top=37000, label_size=25)

    #

    ind = [redis_stat_gen.payload_size_to_int(ds) for ds in data_sizes]
    xtick_labels = [str(int(ds/1000)) for ds in ind]

    bar_plot.plot(
        [clients_avg_set_vals[0],
        clients_avg_get_vals[0]],
        xtick_labels,
        #rotation="vertical",
        yticks_step=10000,
        legends=['SET', 'GET'],
        std_arrs=[clients_std_set_vals[0]
        ,clients_std_get_vals[0]],
        display_val=True)


def tput_redis_benchmark_clients_line_set_get(experiment_dir):
    # Figure 5
    client_num = [1, 64, 128, 256, 512]
    data_sizes = ['1 KB', '50 KB', '100 KB', '500 KB', '1 MB']

    redis_stat_gen = RedisStatGenerator()

    clients_redis_res, _, all_xtick_labels = redis_stat_gen.compare_clients_num(
        os.path.join(
            experiment_dir,
            "redis_benchmark_results",
            "n_1000"
        )
    )

    clients_set_vals = []
    clients_get_vals = []
    for cli_num, cli_dict in clients_redis_res:
        cli_set_val_list = []
        cli_get_val_list = []
        for i, v in enumerate(all_xtick_labels):
            if v in data_sizes:
                cli_set_val_list.append(cli_dict['SET'][i])
                cli_get_val_list.append(cli_dict['GET'][i])
        clients_set_vals.append(cli_set_val_list)
        clients_get_vals.append(cli_get_val_list)

    client_num_str = [str(n) for n in client_num]
    ind = [redis_stat_gen.payload_size_to_int(ds) for ds in data_sizes]

    xtick_labels = [str(int(ds/1000)) for ds in ind]

    line_plot = LinePlot(
        plot_filename="redis_benchmark_tput_line_clients_datasize_set",
        xlabel="Data-sizes (KB)",
        ylabel="Throughput\n(requests/s)",
        legend_loc="best",
        legend_size=25,
        inner_txt_size=20,
        label_size=25
    )

    line_plot.plot(
        clients_set_vals,
        xtick_labels, "--o",
        ind=ind,
        legends=client_num_str,
        legend_title="Number of Clients",
        rotation="vertical",
        ncol=3)

    line_plot = LinePlot(
        plot_filename="redis_benchmark_tput_line_clients_datasize_get",
        xlabel="Data-sizes (KB)",
        ylabel="Throughput\n(requests/s)",
        legend_loc="best",
        legend_size=25,
        inner_txt_size=20,
        label_size=25
    )

    line_plot.plot(
        clients_get_vals,
        xtick_labels, "--o",
        ind=ind,
        legends=client_num_str,
        legend_title="Number of Clients",
        rotation="vertical",
        ncol=3)


def tput_latency_3_apps_local_live_buffered_w_1(experiment_dir):
    # Figure 6
    apps = ["als", "flux_msip", "flux_mscp"]
    data_sizes = ["10mb", "105b", "105b"]
    sources = [1, 2, 2]
    workers = [1]

    xtick_labels = ["Real-time", "Buffered"]

    apps_tput_avg_values = []
    apps_tput_std_values = []
    var1 = "normalized_throughput"

    apps_latency_avg_values = []
    apps_latency_std_values = []
    var2 = "avg_event_time_latency"
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

        apps_tput_avg_values.append(exp_local_live.get_agg_results(var1) +
            exp_local_buffered.get_agg_results(var1))
        apps_tput_std_values.append(exp_local_live.get_agg_results(var1, AggregateMethod.STD) + 
            exp_local_buffered.get_agg_results(var1, AggregateMethod.STD))

        apps_latency_avg_values.append(exp_local_live.get_agg_results(var2) +
            exp_local_buffered.get_agg_results(var2))
        apps_latency_std_values.append(exp_local_live.get_agg_results(var2, AggregateMethod.STD) + 
            exp_local_buffered.get_agg_results(var2, AggregateMethod.STD))

    bar_plot = BarPlot(plot_filename="tput_3_apps_local_live_buffered_w_1",
                       xlabel="Processing Strategy",
                       ylabel="Throughput\n(tasks/s)",
                       inner_txt_size=20,
                       ylim_top=2300, legend_size=20,
                       legend_loc="upper right")

    bar_plot.plot(
        apps_tput_avg_values,
        xtick_labels,
        legends=["ImageAnalysis", "MovingAverage", "ChangeDetection"],
        std_arrs=apps_tput_std_values, ncol=1, display_val=True)

    bar_plot = BarPlot(plot_filename="latency_3_apps_local_live_buffered_w_1",
                       xlabel="Processing Strategy",
                       ylabel="Latency (s)",
                       inner_txt_size=20,
                       ylim_top=2800, legend_size=20,
                       legend_loc="upper left")

    bar_plot.plot(
        apps_latency_avg_values,
        xtick_labels,
        legends=["ImageAnalysis", "MovingAverage", "ChangeDetection"],
        std_arrs=apps_latency_std_values, ncol=1, display_val=True)


def tput_latency_3_apps_2_modes_buffered_w_1_64(experiment_dir):
    # Figure 7 and 9
    apps = ["als", "flux_msip", "flux_mscp"]
    data_sizes = ["10mb", "105b", "105b"]
    sources = [1, 2, 2]
    workers = [1, 4, 8, 16, 32, 64]

    xtick_labels = [str(w) for w in workers]

    var1 = "normalized_throughput"
    var2 = "avg_event_time_latency"
    for i in range(len(apps)):
        exp_local = Experiment(apps[i], data_sizes[i], experiment_dir,
            is_local=True, is_buffered=True)
        if apps[i] == "flux_msip" or apps[i] == "flux_mscp":
            exp_cori = Experiment(apps[i], data_sizes[i], experiment_dir,
               is_local=False, is_buffered=True, scaling_style="strong_scaling")
        else:
            exp_cori = Experiment(apps[i], data_sizes[i], experiment_dir,
                is_local=False, is_buffered=True)

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_local.add_setup(sources[i], workers[j])
            exp_cori.add_setup(sources[i], workers[j])

        exp_local.process()
        exp_cori.process()

        apps_tput_avg_values = [
            exp_local.get_agg_results(var1, method=AggregateMethod.RAW_VAL),
            exp_cori.get_agg_results(var1, method=AggregateMethod.RAW_VAL)
        ]

        apps_latency_avg_values = [
            exp_local.get_agg_results(var2, method=AggregateMethod.RAW_VAL),
            exp_cori.get_agg_results(var2, method=AggregateMethod.RAW_VAL)
        ]

        ylim_top=None
        ncol = 1
        legend_loc = "best"
        if apps[i] == "flux_msip" or apps[i] == "flux_mscp":
            ylim_top = 14000
            legend_loc = "upper left"

        box_plot = BoxPlot(plot_filename="tput_%s_2_modes_buffered_w_1_64" % apps[i],
                           xlabel="Number of Workers",
                           ylabel="Throughput\n(tasks/s)",
                           fig_size1=8, fig_size2=6, font_size=32, label_size=32,
                           legend_size=28, legend_loc=legend_loc, ylim_top=ylim_top)

        box_plot.plot(
            apps_tput_avg_values,
            xtick_labels,
            legends=["Local", "Remote"],
            ncol=ncol
        )

        box_plot = BoxPlot(plot_filename="latency_%s_2_modes_buffered_w_1_64" % apps[i],
                           xlabel="Number of Workers",
                           ylabel="Latency (s)",
                           fig_size1=8, fig_size2=6, font_size=32, label_size=32,
                           legend_size=28, legend_loc="best")

        box_plot.plot(
            apps_latency_avg_values,
            xtick_labels,
            legends=["Local", "Remote"],
            ncol=1
        )


def tput_latency_2_apps_2_modes_live_w_1_64(experiment_dir):
    # Figure 8 and 10
    apps = ["flux_msip", "flux_mscp"]
    data_sizes = ["105b", "105b"]
    sources = [2, 2]
    workers = [1, 4, 8, 16, 32, 64]

    xtick_labels = [str(w) for w in workers]

    var1 = "normalized_throughput"
    var2 = "avg_event_time_latency"
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

        apps_tput_avg_values = [
            exp_local.get_agg_results(var1, method=AggregateMethod.RAW_VAL),
            exp_cori.get_agg_results(var1, method=AggregateMethod.RAW_VAL)
        ]

        apps_latency_avg_values = [
            exp_local.get_agg_results(var2, method=AggregateMethod.RAW_VAL),
            exp_cori.get_agg_results(var2, method=AggregateMethod.RAW_VAL)
        ]

        box_plot = BoxPlot(plot_filename="tput_%s_2_modes_live_w_1_64" % apps[i],
                           xlabel="Number of Workers",
                           ylabel="Throughput\n(tasks/s)",
                           legend_size=25, legend_loc="best")

        box_plot.plot(
            apps_tput_avg_values,
            xtick_labels,
            legends=["Local", "Remote"],
            ncol=1
        )

        box_plot = BoxPlot(plot_filename="latency_%s_2_modes_live_w_1_64" % apps[i],
                           xlabel="Number of Workers",
                           ylabel="Latency (s)",
                           legend_size=25, legend_loc="best")

        box_plot.plot(
            apps_latency_avg_values,
            xtick_labels,
            legends=["Local", "Remote"],
            ncol=1
        )


def tput_3_apps_cori_buffered_w_64_640(experiment_dir):
    # Figure 11
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

        ylim_top = None
        if apps[i] == "als":
            ylim_top = 10
        else:
            ylim_top = 20000
        bar_plot = BarPlot(plot_filename="tput_%s_cori_buffered_w_64_640" % apps[i],
                           xlabel="Number of Workers", ylabel="Throughput\n(tasks/s)",
                           font_size=32, label_size=32,
                           #fig_size1=9, fig_size2=7,
                           ylim_top=ylim_top)

        bar_plot.plot(
            [exp_cori.get_agg_results(var)],
            xtick_labels,
            std_arrs=[exp_cori.get_agg_results(var, AggregateMethod.STD)])


def tput_1_app_cori_buffered_w_128_640_weak_scaling(experiment_dir):
    # Figure 12 A
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
                           ylabel="Throughput\n(tasks/s)",
                           ylim_bottom=0, ylim_top=9000)

        line_plot.plot(
            [exp_cori.get_agg_results(var)],
            xtick_labels,
            "--o")


def tput_1_app_cori_buffered_w_64_throttling(experiment_dir):
    # Figure 12 B
    queue_data_dir = os.path.join(
        experiment_dir,
        "throttling_data"
    )

    all_time_values = []
    all_count_values = []
    for entry in os.scandir(queue_data_dir):
        if entry.is_dir(follow_symlinks=False):
            csv_file = next(os.scandir(entry))
            time_values = []
            count_values = []
            with open(csv_file, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    time_values.append(float(row[0]))
                    count_values.append(int(row[1]))
            first_timestamp = min(time_values)
            time_values = [s-first_timestamp for s in time_values]

            all_time_values.append(time_values)
            all_count_values.append(count_values)

    line_plot = LinePlot(plot_filename="tput_1_app_cori_buffered_w_64_throttling",
                   xlabel="Time (s)",
                   ylabel="Number of tasks\nin queue",
                   ylim_bottom=0, ylim_top=3000,
                   label_size=22, inner_txt_size=19,
                   color_list=['b', 'g', 'r'])

    line_plot.plot_time_data(
        all_time_values,
        all_count_values,
        [':o', ':x', ':^'],
        markevery=50,
        legends=["1500", "2000", "2500"],
        legend_title="Backpressure",
        ncol=1,
        xticks_step=200)
    

def tput_latency_1_app_cori_live_w_640_payload_2_10_mb(experiment_dir):
    # Figure 13
    apps = ["als"]
    data_sizes = ["2mb", "4mb", "6mb", "8mb", "10mb"]
    sources = [1]
    workers = [640]

    xtick_labels = data_sizes

    apps_tput_avg_values = []
    apps_tput_std_values = []
    apps_latency_avg_values = []
    apps_latency_std_values = []
    tput_var = "normalized_throughput"
    latency_var = "avg_event_time_latency"
    for i in range(len(data_sizes)):
        exp_cori = Experiment(apps[0], data_sizes[i], experiment_dir,
            is_local=False, is_buffered=False)

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_cori.add_setup(sources[j], workers[j])

        exp_cori.process()

        apps_tput_avg_values.append(exp_cori.get_agg_results(tput_var, AggregateMethod.MEAN)[0])
        apps_tput_std_values.append(exp_cori.get_agg_results(tput_var, AggregateMethod.STD)[0])
        apps_latency_avg_values.append(exp_cori.get_agg_results(latency_var, AggregateMethod.MEAN)[0])
        apps_latency_std_values.append(exp_cori.get_agg_results(latency_var, AggregateMethod.STD)[0])

    bar_plot = BarPlot(plot_filename="tput_%s_cori_live_w_640_payload_2_10_mb" % apps[0],
                       xlabel="Data-sizes (MB)",
                       ylabel="Throughput\n(tasks/s)",
                       ylim_top=10)

    bar_plot.plot(
        [apps_tput_avg_values],
        xtick_labels,
        std_arrs=[apps_tput_std_values]
    )

    bar_plot = BarPlot(plot_filename="latency_%s_cori_live_w_640_payload_2_10_mb" % apps[0],
                       xlabel="Data-sizes (MB)",
                       ylabel="Latency (s)",
                       ylim_bottom=0)

    bar_plot.plot(
        [apps_latency_avg_values],
        xtick_labels,
        std_arrs=[apps_latency_std_values]
    )


def tput_2_apps_cori_live_w_64_pipeline_vs_non_pipeline(experiment_dir):
    # Figure 14
    apps = ["als", "flux_msip"]
    data_sizes = ["1kb", "105b"]
    sources = [1, 2]
    workers = [64]

    xtick_labels = ["ImageAnalysis", "MovingAverage"]

    avg_tput_default_vals = []
    avg_tput_pipeline_vals = []
    std_tput_default_vals = []
    std_tput_pipeline_vals = []

    var = "normalized_throughput"
    for i in range(len(apps)):
        exp_cori_default = Experiment(apps[i], data_sizes[i], experiment_dir,
            is_local=False, is_buffered=False, is_pipeline=False)
        exp_cori_pipeline = Experiment(apps[i], data_sizes[i], experiment_dir,
            is_local=False, is_buffered=False, is_pipeline=True)

        for j in range(len(workers)):
            # Adding Setup convention telling how many sources
            # and workers were running for that experiment
            exp_cori_default.add_setup(sources[i], workers[j])
            exp_cori_pipeline.add_setup(sources[i], workers[j])

        exp_cori_default.process()
        exp_cori_pipeline.process()

        avg_tput_default_vals.append(exp_cori_default.get_agg_results(var)[0])
        avg_tput_pipeline_vals.append(exp_cori_pipeline.get_agg_results(var)[0])
        std_tput_default_vals.append(exp_cori_default.get_agg_results(var, AggregateMethod.STD)[0])
        std_tput_pipeline_vals.append(exp_cori_pipeline.get_agg_results(var, AggregateMethod.STD)[0])
 
    bar_plot = BarPlot(plot_filename="tput_2_apps_cori_live_w_64_pipeline_vs_non_pipeline",
                       xlabel="Applications",
                       ylabel="Throughput\n(tasks/s)",
                       inner_txt_size=20, legend_size=25,
                       ylim_top=5000)

    bar_plot.plot(
        [avg_tput_default_vals, avg_tput_pipeline_vals],
        xtick_labels,
        legends=["non-pipeline", "pipeline"],
        std_arrs=[std_tput_default_vals, std_tput_pipeline_vals],
        display_val=True,
        ncol=1)


def main(args):
    experiment_dir = args.experiment_dir
    figure_num = args.figure_num

    if figure_num == 0:
        tput_redis_benchmark_bar_set_get(experiment_dir)
        tput_redis_benchmark_clients_line_set_get(experiment_dir)
        tput_latency_3_apps_local_live_buffered_w_1(experiment_dir)
        tput_latency_3_apps_2_modes_buffered_w_1_64(experiment_dir)
        tput_latency_2_apps_2_modes_live_w_1_64(experiment_dir)
        tput_3_apps_cori_buffered_w_64_640(experiment_dir)
        tput_1_app_cori_buffered_w_128_640_weak_scaling(experiment_dir)
        tput_1_app_cori_buffered_w_64_throttling(experiment_dir)
        tput_latency_1_app_cori_live_w_640_payload_2_10_mb(experiment_dir)
        tput_2_apps_cori_live_w_64_pipeline_vs_non_pipeline(experiment_dir)
    elif figure_num == 4:
        tput_redis_benchmark_bar_set_get(experiment_dir)
    elif figure_num == 5:
        tput_redis_benchmark_clients_line_set_get(experiment_dir)
    elif figure_num == 6:
        tput_latency_3_apps_local_live_buffered_w_1(experiment_dir)
    elif figure_num == 7 or figure_num == 9:
        tput_latency_3_apps_2_modes_buffered_w_1_64(experiment_dir)
    elif figure_num == 8 or figure_num == 10:
        tput_latency_2_apps_2_modes_live_w_1_64(experiment_dir)
    elif figure_num == 11:
        tput_3_apps_cori_buffered_w_64_640(experiment_dir)
    elif figure_num == 12:
        tput_1_app_cori_buffered_w_128_640_weak_scaling(experiment_dir)
        tput_1_app_cori_buffered_w_64_throttling(experiment_dir)
    elif figure_num == 13:
        tput_latency_1_app_cori_live_w_640_payload_2_10_mb(experiment_dir)
    elif figure_num == 14:
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
