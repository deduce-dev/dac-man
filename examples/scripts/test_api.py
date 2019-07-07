import dacman
from dacman.plugins.default import DefaultPlugin
import sys

def diff1(file1, file2):
    comparisons = [(file1, file2)]
    differ = dacman.DataDiffer(comparisons, dacman.Executor.DEFAULT)
    differ.use_plugin(DefaultPlugin)
    differ.start()

if __name__ == '__main__':
    diff1(sys.argv[1], sys.argv[2])