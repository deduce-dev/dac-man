# Deduce-Stream
A framework for processing scientific data streams at scale

Deduce-Stream provides the right computing elements that allow:
1. Streaming scientific data
2. Real-time user-specified analysis processing to the data stream

Note: This branch was added to include all the code that we used for testing
and performing benchmark experiments for Deduce-Stream:
```
cd experiments/
```

### Redis

A Redis-server is **needed and must be installed** to serve as a broker/cache for Deduce-Steam framework. The framework was tested on Redis server version=5.0.1, and redis-py 3.5.

For installation, you can follow [The Redis quickstart documentation](https://redis.io/topics/quickstart)

Redis could also be installed using the command line
```sh
$ apt-get install redis # ubuntu
$ dnf install redis # fedora 
$ brew install redis # osx
```

To install Redis on Windows follow these [instructions](https://redislabs.com/blog/redis-on-windows-10).

### Installation
Deduce-Stream is implemented in Python 3.

```
python3 setup.py install
```

## Transforming Data Streams
`deduce_stream` provides the capabilities to stream scientific data to a broker/cache (currently only Redis is supported)
to be analyzed in real-time by processing units.

`deduce_stream` supports two sets of streaming applications:
1. Independent streams - in which data analysis is performed on singular streams independently.
2. Dependent streams - in which data analysis is performed on intercorrelated streams, where multiple streams are needed for an analysis task creation.

### Independent streams - `StreamSrc`
`deduce_stream` implemented a `StreamSrc` class for independent streams that don't have any correlation with each other,
at least one single stream is required.

```python
from deduce_stream import StreamSrc

stream_src = StreamSrc()
stream_src.set_cache(host, port) # Redis host & port
```

### Dependent streams - `WindowedStreamSrc`
This class is implemented for dependent intercorrelated streams.
For example, if we have multiple data sensors from around the globe that measure temperature,
and we need to analyze these measurements together, then `WindowedStreamSrc` would be the best option for this.
At lease two streams are required for this option.

We chose the concept of Windows because multiple streams could submit data records into the same window.
And when a certain user-specified window size is reached, an analysis task is created within `deduce_stream`

```python
from deduce_stream import WindowedStreamSrc

stream_src_1 = WindowedStreamSrc()
stream_src_1.set_cache(host, port) # Redis host & port

# window_key is the naming convention that all related streams should agree
# on to submit data to. For example, timestamp could be a uniquely named Window
# e.g key_name = 'timestamp', and the window name would be '1598899648' for example.
stream_src_1.set_window_key(key_name)

# Window size signals when the Window is full and a task needs to be created
stream_src_1.set_window_size(window_size)
```

Another related source will be pushing to the same window to form interconnected analysis tasks (e.g comparing
temperatures in two different locations where both sensors share the same timestamp/key_name ):

```python
from deduce_stream import WindowedStreamSrc

stream_src_2 = WindowedStreamSrc()
stream_src_2.set_cache(host, port) # Redis host & port
stream_src_2.set_window_key(key_name)
stream_src_2.set_window_size(window_size) # window_size = 2, if we have 2 sensors each sending 1 temperature value
```

### Data Iterator
Users have to specify data iterators for `deduce_stream`. This is the step where we connect
the data source generator with the `*StreamSrc` APIs for stream handling.

An example of a user defined `data_iterator`
```python
# streaming data from a dataset on disk
def data_iterator(dataset):
    df = pd.read_csv(dataset, comment='#', sep=',', na_filter=False, dtype='str')
    dataset_len = len(df.index)
    for i in range(1, dataset_len):
        data_points = df.loc[i-1:i]
        yield data_points.tolist()

dataset = "path/to/csv_file.csv"

stream_src = StreamSrc()
stream_src.set_cache(host, port) # Redis host & port
stream_src.set_dataset_iterator(data_iterator)
stream_src.stream(dataset) # the arguments passed here is the arguments data_iterator expects
```

#### datablock

The data iterator function should yield a list of datablocks needed to formulate an analysis task
to be processed by workers. A **datablock** is our defined term to define a single processable
unit that the user sees fit. A datablock could be in the form of `int`, `float`, `str`, or 
any form that `redis-py` is able to convert to bytes (This might change in the future as we
support other cache technologies other than Redis). But it is advised that the users convert
their datablocks into bytes themselves if they have more complex datatypes, e.g `arrays` or
`class objects`. These bytes will be streamed to and stored in the specified cache. The user
is responsible to implement the
[Analysis Operator](https://github.com/deduce-dev/deduce_stream#analysis-operator) (mentioned below)
in a way that unpacks the datablock bytes into its original form for analysis.

For example:
```python
# This is a mockup of a light source stream sending a
# sequence of frames
def transform_stream(n_frames=100, image_size=1000):
    frameA = np.random.rand(image_size)

    for i in range(1, n_frames):
        frameB = np.random.rand(image_size)
        yield [frameA.tobytes(), frameB.tobytes()]
        frameA = frameB

stream_src = StreamSrc()
stream_src.set_cache(host, port) # Redis host & port
stream_src.set_dataset_iterator(data_iterator)
stream_src.stream()
```

In the above example the data iterator `transform_stream` yields two datablocks `frameA` & `frame2`.
These two yielded datablocks formulate a task to be processed by a
[worker](https://github.com/deduce-dev/deduce_stream#analysis-operator).


## Real-time Analysis
`deduce_stream` supports real-time analysis. Multiple processing units (workers) could be instantiated
to perform data analysis tasks parallelly in real-time. These workers connect to the specified
broker/cache (currently only Redis is supported) to pull tasks from. And the workers send back the results
to the same cache after the analysis computation is done.

### Workers - `StreamProcessingWorker`
`StreamProcessingWorker` is `deduce_stream`'s main implementation for a worker. Initiating a worker is straightforward:

```python
from deduce_stream import StreamProcessingWorker

worker = StreamProcessingWorker()
worker.set_cache(host, port) # Redis host & port
```

### Analysis Operator
To be able to perform the correct analysis, users have to specify an analysis operator
to be performed by the workers.

To continue the above light source example:
```python
# in this example, a task contains two datablocks (frameA & frameB) to be analyzed
def image_analysis(frameA, frameB):
    matrix1 = np.frombuffer(frameA)
    matrix2 = np.frombuffer(frameB)
    
    # compute RMSE between the 2 input frames
    rms = sqrt(mean_squared_error(matrix1, matrix2))
    # logarithm of RMSE
    rms_log = np.log(rms) 

    t_test_t, t_test_p = stats.ttest_ind(matrix1, matrix2, equal_var=True)
    
    return np.asarray([rms_log, t_test_t, t_test_p]).tobytes()

worker = StreamProcessingWorker()
worker.set_cache(host, port) # Redis host & port
worker.set_analysis_operator(image_analysis)
worker.process()
```

The workers send the returned analysis results back to the cache (currently Redis) to be picked up by the users.

For example to look at a certain task result that was processed by a worker:
```sh
$ redis-cli -h <host> -p <port>
127.0.0.1:6379> GET "task:bce28e8e-06ab-4a7b-8a55-9cd7f3b40de6" # task-id
```

## Interacting with Redis

There's a Task Ordered list `job_ordered_list:<id>` (created on Redis) for the sole purpose of knowing the order of the tasks that were
pushed to the Task Queue. So to get the results back in order, it is necessary to retrieve the task-id list:

```sh
$ redis-cli -h <host> -p <port>
127.0.0.1:6379> KEYS job_ordered_list*
1) "job_ordered_list:25b5ace4a8de734123e1d0e49dbde93ed6d2a0c9"
127.0.0.1:6379> LLEN "job_ordered_list:25b5ace4a8de734123e1d0e49dbde93ed6d2a0c9"
(integer) 198 # Total number of tasks that were sent by the streaming source(s)
127.0.0.1:6379> lrange "job_ordered_list:25b5ace4a8de734123e1d0e49dbde93ed6d2a0c9" 0 -1 # 0 is the start, -1 is the end (Whole list in that case)
  1) "task:bce28e8e-06ab-4a7b-8a55-9cd7f3b40de6"
  2) "task:83e5fe28-9ce4-4587-b5de-44c7aea562b5"
  3) "task:a472416a-e4d1-4d64-a314-c9fddb4be73c"
  4) "task:2cc1dd3f-c9d2-4921-b86f-100412373b7d"
  5) "task:a03836e7-8c67-4103-954c-8e65244d8a6c"
  6) "task:024e47ff-dffc-444a-824c-f7028e1b5faf"
  7) "task:9e759ea9-f6a3-43e8-bc73-fd5c85ff7869"
  8) "task:c335e792-f464-4dcc-9ff2-3eadd6113f55"
  9) "task:30e93489-e056-40ab-a912-c2d9454b34bb"
 10) "task:20fc577d-c3d9-4143-93eb-275f61b79f04"
                        .
                        .
                        .
196) "task:4e10d8de-b60e-4925-ae97-11090b1c28d5"
197) "task:2be01e55-1f8d-4a1c-be42-82558b5ef2d5"
198) "task:6d7748db-bdd2-4dbc-9bd1-eef3a1b7be10"
```

In order to control the naming conventions used (e.g `job_ordered_list` for the Task Ordered list), you can directly edit the variables
in `deduce_stream/setting.py` before installing `deduce_stream`.

`deduce_stream/setting.py`
```python
# Main naming convention
DATABLOCK_PREFIX="datablock"
TASK_PREFIX="task"
TASK_QUEUE_NAME="task_queue"
JOB_ORDERED_LIST="job_ordered_list"
```
