#!/usr/bin/env python3

## pylint: disable=too-many-locals

import os

from collections import defaultdict, namedtuple
from statistics import mean, median, pstdev

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT      = "/home/charles/Projects/cambridge_property_db/"
STATS     = os.path.join(ROOT, "stats")
GRAPHS    = os.path.join(ROOT, "graphs")
DATA_PATH = os.path.join(STATS, "lots_all.csv")


ZONES_RES = {
    "A-1": 0.5,
    "A-2": 0.5,
    "B": 0.5,
    "C": 0.6,
    "C-1": 0.75,
}
ZONES = ZONES_RES

Stats = namedtuple('Stats', ['mean', 'median', 'max', 'stddev', 'quantiles'])

def getStats(data, res=2):
    stats = [round(x, res) for x in (mean(data), median(data), max(data), pstdev(data))]
    stats.append([round(x, res) for x in np.quantile(data, q=np.arange(.01, 1.00, .01))])
    return Stats(*stats)


def main():
    data = pd.read_csv(DATA_PATH, index_col='id')
    zone_values = data['zone']
    zones = [x for x in zone_values.unique() if 'SD-' not in x]
    for zone in zones:
        if ZONES and zone not in ZONES:
            continue

        ## Get data
        zone_data = data[zone_values == zone]
        far_values = zone_data['FAR'].to_numpy()
        stats = getStats(far_values)

        ## Make graph
        plt.hist(far_values, color='lightblue', ec='black', bins=15)
        plt.title(f"FAR Distribution - Zone {zone}")
        plt.xlabel("FAR")
        plt.ylabel("Number of Lots")

        ## Make lines
        min_ylim, max_ylim = plt.ylim()
        min_xlim, max_xlim = plt.xlim()
        txt_offset = max_xlim * 0.01
        far_limit = ZONES[zone]
        plt.axvline(far_limit, color='red', linestyle='dashed', linewidth=2, zorder=99)
        plt.text(
            far_limit+txt_offset,
            max_ylim*0.9,
            '{:.2f}'.format(far_limit),
            fontweight='bold',
            horizontalalignment='left',
            backgroundcolor='white',
            zorder=98,
        )

        plt.axvline(stats.median, color='orange', linestyle='dashed', linewidth=2, zorder=97)
        plt.text(
            stats.median+txt_offset,
            max_ylim*0.8,
            '{:.2f}'.format(stats.median),
            fontweight='bold',
            horizontalalignment='left',
            backgroundcolor='white',
            zorder=96
        )

        per_75 = stats.quantiles[74]
        plt.axvline(per_75, color='darkblue', linestyle='dashed', linewidth=2, zorder=95)
        plt.text(
            per_75+txt_offset,
            max_ylim*0.7,
            '{:.2f}'.format(per_75),
            fontweight='bold',
            backgroundcolor='white',
            zorder=94,
        )

        ## Show
        plt.savefig(os.path.join(GRAPHS, f"zone_{zone}.png"))
        plt.clf()

main()
