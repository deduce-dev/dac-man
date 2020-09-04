from deduce_stream.cache import Cache

# StreamSource Implementation
class StreamSrc(object):
    """Defines a single stream source

    This class handles streaming data to a cache/broker (set by the user)
    and organizes streams into analysis tasks that is picked up by
    processing workers.
    """
    def __init__(self):
        self.cache = None
        self.dataset_iterator = None

        self.stats_dir = None

    def set_cache(self, host, port):
        """Sets cache/broker (Currently only Redis is supported)

        Parameters
        ----------
        host : str
            cache host address
        port : int
            cache port
        """
        self.cache = Cache(host, port)

    def delete_cache(self):
        """Unset cache"""
        self.cache = None

    def set_stats_dir(self, stats_dir):
        """Sets stats directory

        Parameters
        ----------
        stats_dir : str
            stats directory for benchmarking results
        """
        self.stats_dir = stats_dir

    def set_dataset_iterator(self, fn):
        """Sets data iterator/generator function

        Sets a user specified callback function. This callback
        should yield datablocks that in total forms the data
        stream. A datablock is our defined term to define a single
        processable unit that the user sees fit.

        Parameters
        ----------
        fn : Callable
            A function that yields datablocks 
        """
        self.dataset_iterator = fn

    def data_send(self, datablocks):
        """Sends datablocks to cache

        Firstly, this function sends a list of user specified datablocks
        to the cache and retrieves a list of datablock-ids for each datablock.
        Secondly, data_send use these ids to create tasks in the cache's
        TaskQueue.

        Parameters
        ----------
        datablocks : list
            A list of user specified datablocks
        """
        datablock_ids = self.cache.put_multi_datablocks(datablocks)
        self.cache.create_task(*datablock_ids)

    def stream(self, *stream_args):
        """Main Streaming Engine

        Parameters
        ----------
        stream_args : list
            A list of arguments to be passed to the dataset iterator if
            the user deems necessary. e.g datafile path to read from
        """
        if not self.cache:
            raise NotImplementedError("A cache must be set. Use .set_cache(host, port). "
                             "Currently only Redis is supported.")

        if not self.dataset_iterator:
            raise NotImplementedError("dataset_iterator must be set")

        stream_gen = self.dataset_iterator(*stream_args)

        while True:
            try:
                datablocks = next(stream_gen)
                self.data_send(datablocks)
            except StopIteration:
                break

        if self.stats_dir is not None:
            self.cache.write_streaming_source_stats(self.stats_dir)


class WindowedStreamSrc(StreamSrc):
    """Defines a single stream source that streams data in Windows

    This class handles streaming data to a cache/broker (set by the user).
    However, this is different from 'StreamSrc' where a single stream
    cannot create tasks on it's own. It needs other streams to formulate
    tasks. The idea is implemented by having multiple streams push
    their datablock ids into a common Window (e.g A Redis list), and a
    task is created when that Window reaches a certain size. For example,
    having two temperature sensors that we want to compare their values
    together.
    """
    def __init__(self):
        super().__init__()
        self.window_key = None
        self.window_size = 2

    def set_window_key(self, window_key):
        """Sets a main window key

        A window key is the main feature that unites streams together. For
        example, a common window key would be a timestamp string. This is
        a good choice because we can compare values collected at the same
        time from different facilities or sensors. However, the users can
        specify what they see fit.

        Parameters
        ----------
        window_key : std
            user specified window key to combine multiple streams at.
        """
        self.window_key = window_key

    def set_window_size(self, window_size):
        """Sets the window size

        The window size determines when the Window is full/complete and a
        task is ready to be created for workers to process.

        Parameters
        ----------
        window_size : int
            A window size to specify when the Window is full/complete.
        """
        self.window_size = window_size

    def data_send(self, win_key, datablocks):
        """Sends datablocks to cache

        Firstly, this function sends a list of user specified datablocks
        to the cache and retrieves a list of datablock-ids for each datablock.
        Secondly, data_send send these ids to a Window with the actual win_key
        value (e.g 1598593841 -> timestamp). If the window size is reached, a
        task is created in the cache's TaskQueue.

        Parameters
        ----------
        win_key: str
            The actual window key value to send the datablocks ids at.
        datablocks : list
            A list of user specified datablocks.
        """
        datablock_ids = self.cache.put_multi_datablocks(datablocks)
        self.cache.assign_datablocks_to_window(win_key, datablock_ids)

        n_datablocks = self.cache.get_current_window_size(win_key)
        if n_datablocks == self.window_size:
            datablock_ids = self.cache.get_windowed_datablock_ids(win_key)
            assert len(datablock_ids) == self.window_size, \
                "Actual window size: %d > intended window size: %d" \
                    % (self.cache.get_current_window_size(win_key), self.window_size)
            self.cache.create_task(*datablock_ids)

    def stream(self, *stream_args):
        """Main Streaming Engine

        Parameters
        ----------
        stream_args : list
            A list of arguments to be passed to the dataset iterator if
            the user deems necessary. e.g datafile path to read from
        """
        if not self.cache:
            raise NotImplementedError("A cache must be set. Use .set_cache(host, port). "
                             "Currently only Redis is supported.")

        if not self.window_key:
            raise NotImplementedError("window key must be set")

        if not self.dataset_iterator:
            raise NotImplementedError("dataset_iterator must be set")

        stream_gen = self.dataset_iterator(*stream_args)

        for window_key_val, datablocks in stream_gen:
            self.data_send(window_key_val, datablocks)

        if self.stats_dir is not None:
            self.cache.write_streaming_source_stats(self.stats_dir)
