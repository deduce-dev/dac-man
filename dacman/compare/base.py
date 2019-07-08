import abc
import numpy


class DacmanRecordAdaptor(abc.ABC):
    @abc.abstractmethod
    def transform(self, data_file):
        return

    def __flatten_ndarray__(self, ndarray):
        if type(ndarray) == numpy.ndarray:
            flat_array = ndarray.flatten()
            flat_array = flat_array.tolist()
            return flat_array
        else:
            array = numpy.asarray(ndarray)
            flat_array = []
            for row in array:
                flat_array.append(repr(row))

            flat_array = numpy.asarray(flat_array)
            return flat_array


class Comparator(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def supports(self):
        return

    @staticmethod
    @abc.abstractmethod
    def description(self):
        return

    @abc.abstractmethod
    def compare(self, a, b, *args):
        """
        :param a: comparable data
        :param b: data to compare against
        :param args: any additional params for comparing a and b
        :return: data change results
        """
        return

    @abc.abstractmethod
    def percent_change(self):
        """
        :return: percentage change between a and b
        """
        return

    @abc.abstractmethod
    def stats(self, changes):
        # min_change = min(changes)
        # max_change = max(changes)
        # summary_change = summarize(changes)
        return




