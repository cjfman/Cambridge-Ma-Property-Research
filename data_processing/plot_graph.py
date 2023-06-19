#!/usr/bin/env python3

## pylint: disable=too-many-locals

import os

from collections import namedtuple
from statistics import mean, median, pstdev

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT      = "/home/charles/Projects/cambridge_property_db/"
STATS     = os.path.join(ROOT, "stats")
GRAPHS    = os.path.join(ROOT, "graphs")
DATA_PATH = os.path.join(STATS, "lots_all.csv")
OVERWRITE = False


ZONES = {
    "A-1": 0.5,
    "A-2": 0.5,
    "B": 0.5,
    "C": 0.6,
    "C-1": 0.75,
    "BA": 1.75,
    "BA-1": 1.00,
    "BA-2": 1.75,
    "BA-3": 1.75,
    "BA-4": 1.75,
    "BB": 3,
    "BB-1": 3.24,
    "BB-2": 3.0,
    "BC": 2.0,
}

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

        out_path = os.path.join(GRAPHS, f"zone_{zone}.png")
        if os.path.isfile(out_path) and not OVERWRITE:
            continue

        ## Get data
        zone_data = data[zone_values == zone]
        far_values = zone_data['FAR'].to_numpy()
        stats = getStats(far_values)

        ## Make graph
        fig, axs = plt.subplots(2, 2, tight_layout=False)
        plot_data_sets = [
            ("Median", stats.median),
            ("75th Percentile", stats.quantiles[74]),
            ("80th Percentile", stats.quantiles[79]),
            ("90th Percentile", stats.quantiles[89]),
        ]

        for i, plot_data in enumerate(plot_data_sets):
            title, line_value = plot_data
            title = f"FAR Distribution - Zone {zone}\n{title}"
            plotHist(axs[i//2][i%2], title, far_values, ZONES[zone], line_value)

        ## Show
        #plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
        plt.savefig(out_path)
        #plt.show()
        plt.clf()


def plotHist(axs, title, values, far_limit, line_value):
    print(axs)
    axs.hist(values, color='lightblue', ec='black', bins=15)
    axs.set_title(title)
    axs.set_xlabel("FAR")
    axs.set_ylabel("Number of Lots")
    min_ylim, max_ylim = axs.get_ylim()
    min_xlim, max_xlim = axs.get_xlim()
    txt_offset = max_xlim * 0.01
    line_data_sets = [
        (far_limit, txt_offset, max_ylim*0.8, 'red', False),
        (line_value, txt_offset, max_ylim*0.5, 'darkblue'),
    ]
    line_data_sets.sort()
    zorder = 100
    for line_data in line_data_sets:
        plotLine(axs, *line_data, zorder=zorder)
        zorder -= 2


def plotLine(axs, value, x_offset, y, color, show_text=True, *, zorder=2):
    axs.axvline(value, color=color, linestyle='dashed', linewidth=2, zorder=zorder)
    if show_text:
        axs.text(value + x_offset, y, '{:.2f}'.format(value),
            fontweight='bold',
            horizontalalignment='left',
            backgroundcolor='white',
            zorder=zorder-1,
        )

main()
