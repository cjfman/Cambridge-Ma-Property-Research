from collections import namedtuple
from statistics import mean, median, pstdev

import numpy as np

Stats = namedtuple('Stats', ['mean', 'median', 'max', 'min', 'stddev', 'quantiles'])

def getStats(data, res=2, reverse=False):
    stats = [round(x, res) for x in (mean(data), median(data), max(data), min([x for x in data if x >= 0]), pstdev(data))]
    stats.append([round(x, res) for x in np.quantile(data, q=np.arange(.01, 1.00, .01))])

    stats = Stats(*stats)
    if reverse:
        stats.quantiles.sort(reverse=True)

    return stats


def statsSummary(stats, quantiles=(75, 80, 90)):
    metrics = [
        ('Min', stats.min),
        ('Max', stats.max),
        ('Median', stats.median),
    ]
    for quantile in quantiles:
        metrics.append((f"'Pecentile {quantile}'", stats.quantiles[quantile-1]))

    return "; ".join([f"{x}: {y}" for x, y in metrics])
