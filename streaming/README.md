# Run Experiments
# locally
This is a small guide to show as a sample how we evaluated our streaming systems. Each component we used is packaged in this folder `streaming`.

## services
Each component and its code is packaged as a `docker service` in the `services` folder. A `Dockerfile` exists in each service folder to show how the `docker service image` was built.

## compose
A sample orchestration of the evaluation experiments is done using `docker-compose`. For each application, a `docker-compose.yml` file exists to demonstrate how the services were properly connected and evaluated.

### To run a `MovingAverage` experiment
Before we run an experiment using the provided `docker-compose.yml` files, we need to specify which directory we want the experiment results to be written to. We do this by setting this environment variable:
```
$ export SHARED_HOST_DIR=/your/path/choice/for/results
```

Note that `Docker` and `docker-compose` are needed to complete the following steps:
```
$ cd compose/moving_average/
$ docker-compose up
```

The experiment should be starting at this point and you should be seeing text in the standart output that looks like this:
```
$ docker-compose up
Creating network "moving_average_default" with the default driver
Creating moving_average_broker_1 ... done
Creating moving_average_lathuile_1 ... done
Creating moving_average_worker_1   ... done
Creating moving_average_fluxnet_1  ... done
Attaching to moving_average_broker_1, moving_average_worker_1, moving_average_fluxnet_1, moving_average_lathuile_1
broker_1    | 1:C 21 Apr 2020 08:26:48.311 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
broker_1    | 1:C 21 Apr 2020 08:26:48.311 # Redis version=5.0.1, bits=64, commit=00000000, modified=0, pid=1, just started
broker_1    | 1:C 21 Apr 2020 08:26:48.311 # Configuration loaded
broker_1    | 1:M 21 Apr 2020 08:26:48.312 * Running mode=standalone, port=6379.
broker_1    | 1:M 21 Apr 2020 08:26:48.312 # WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
broker_1    | 1:M 21 Apr 2020 08:26:48.312 # Server initialized
broker_1    | 1:M 21 Apr 2020 08:26:48.312 # WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
broker_1    | 1:M 21 Apr 2020 08:26:48.312 # WARNING you have Transparent Huge Pages (THP) support enabled in your kernel. This will create latency and memory usage issues with Redis. To fix this issue run the command 'echo never > /sys/kernel/mm/transparent_hugepage/enabled' as root, and add it to your /etc/rc.local in order to retain the setting after a reboot. Redis must be restarted after THP is disabled.
broker_1    | 1:M 21 Apr 2020 08:26:48.312 * Ready to accept connections
worker_1    | Host:2caa09e50b32-PID:1 is processing task: b"('task:f71b2568-8c48-4f5a-a1b0-eff67de07f2b', 'datablock:c1dba978-8394-498e-9875-49e7f2f4a494', 'datablock:3f38b3d2-b3a5-41af-b870-624938b35e98', 'custom')"
worker_1    | 
worker_1    | Host:2caa09e50b32-PID:1 is processing task: b"('task:1363a56c-9cfc-4092-a5b4-19128e414e0c', 'datablock:3248ddb0-cb44-4712-9bff-b04a2c060ea0', 'datablock:0401b52a-0618-4450-9d8a-90bac6c52eb7', 'custom')"
worker_1    | 
worker_1    | Host:2caa09e50b32-PID:1 is processing task: b"('task:4dfad5de-d90e-4a7f-bab8-2e58f5549250', 'datablock:e1e192a8-506e-4972-8b56-1201c6a46d62', 'datablock:c0504588-27e9-48a9-8369-3361e1e65c6a', 'custom')"
```

### Scaling up workers
To scale the number of workers processing tasks, run this command:
```
$ docker-compose up --scale worker=4
```

After the workers are done processing all streamed tasks, you will see results written in `${SHARED_HOST_DIR}/results`

Wait for all workers to exit to fully see the results. However, you have to manually close the docker-compose run using `ctrl-c` because it won't exit on its own as the broker service will be still running as a `redis-server`.

### Understanding results
In this section, when we refer to data we are talking about timestamps that are saved in different stages in the experiment. This helps us evaluate the system performance.

Under the `results` folder, we'll find two folders: `sources` & `workers`.

#### sources
`sources` folder has all the data saved by the streaming sources that streamed tasks to the broker

#### workers
`workers` folder has all the data saved by all workers that processed the streamed tasks

## plot_generator
This has the code that we used to generate all the figures used in the paper, including a `Dockerfile` for easy packaging.

To generate the graphs run this command:
```
$ cd plot_generator/
$ python3 main.py -e /path/to/dataset/
```

Note: You may need to change the path where the graphs will be generated in settings.py module.

Or to run it with docker:
```
$ docker run -it --rm -v /path/to/dataset:/data aaelbashandy/plot_generator:0.2 python3 main.py -e /data
```

We also can specify what figure number we need to plot using `-f` option:
```
$ python3 main.py -e /path/to/dataset/ -f 4
```
or
```
$ docker run -it --rm -v /path/to/dataset:/data aaelbashandy/plot_generator:0.1 python3 main.py -e /data -f 4
```

Note that `-f 0` will plot all the figures in the paper.

# On HPC
Note: source data for streaming need to be downloaded from the specified websites.

For running the experiments on HPC, users need to configure and launch the HPC containers. We used Shifter for running our experiments on Cori. Shifter is a software package that allows user-created docker images to run at Cori. Shifter has access to publicly published docker images on Docker Hub. We have 3 separate docker images that represent each component in our defined architecture: streaming source, Redis-server, application-worker. A streaming-source container reads a dataset that the user provides. A Redis-server container hosts Redis. A Worker can read tasks + datablocks from the specified Redis. In our experiments, we hosted the streaming source and Redis components on a standalone server and had the application-workers running on Cori. 
As for Redis, the right ports need to be exposed for outer containers to be able to connect to it. Exposing ports in Docker allows containers to be connected to through these specified ports. For instance, the main port that Redis uses to listen to connections is "6379"; but in Docker this port isn't allowed to be seen outside the container unless we specifically expose this port. For example, this launches a Redis container with an exposed port  `docker run -p ${PORT}:6379 redis`.

To be able to launch each of the mentioned components, we first must have Docker/Shifter pull each component image:

- Standalone Server: `docker pull repo-name/streaming-source:tag`
- Standalone Server: `docker pull repo-name/redis:tag`
- Cori: `shifterimg pull repo-name/app-worker:tag`

Now we are ready to connect all components together:
Note: Understandably, Streaming source is different based on each application.

- Standalone Server: To launch a Redis-server: `docker run -p ${PORT}:6379 redis`
- Standalone Server: To launch a single streaming source: `docker run repo-name/streaming-source:tag python3 source.py ${REDIS_HOST} ${REDIS_PORT} ${DATASET} ${STREAMING_TIME} ${MAX_JOB_NUM} ${DATA_FRACTION} ${SOURCE_RESULTS_DIR}`
- Cori: To run for example 10 worker instances on a single Node: `srun -N 1 -n 10 -C ${ARCHITECTURE} --qos=${QUEUE} shifter python3 worker.py ${REDIS_HOST} ${REDIS_PORT} ${TASK_QUEUE} ${WORKER_WAIT_TIME} ${WORKER_RESULTS_DIR}`

This of course assumes that the user will have access on the ip address of the newly created Redis-server `${REDIS_HOST}`. The setup needs to be configured properly.
