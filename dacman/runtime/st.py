from dacman.compare.data import diff


def run(comparisons, plugin):
    results = []
    for comparison in comparisons:
        print(comparison)
        argv = []
        if len(comparison) > 2:
            argv = comparison[2:]
        result = diff(comparison[0], comparison[1], *argv, comparator_plugin=plugin)
        results.append(result)