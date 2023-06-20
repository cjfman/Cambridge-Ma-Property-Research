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
OVERWRITE = True


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

def main():
    #plotZones()
    plotAreas()


def getStats(data, res=2):
    stats = [round(x, res) for x in (mean(data), median(data), max(data), pstdev(data))]
    stats.append([round(x, res) for x in np.quantile(data, q=np.arange(.01, 1.00, .01))])
    return Stats(*stats)


def plotZones():
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
        plotKeyData('FAR', f"Zone {zone}", zone_data, limit=ZONES[zone])

        plt.savefig(out_path)
        #plt.show()
        plt.clf()


def plotAreas():
    data = pd.read_csv(DATA_PATH, index_col='id')
    area_values = data['neighborhood']
    areas = area_values.unique()
    for area in areas:
        clean = area.lower()
        for x in [' ', '/']:
            clean = clean.replace(x, '_')

        out_path = os.path.join(GRAPHS, f"neighborhood_{clean}.png")
        if os.path.isfile(out_path) and not OVERWRITE:
            continue

        ## Get data
        area_data = data[area_values == area]
        print(f"Plotting data for neighborhood {area}")
        plotKeyData('FAR', area, area_data)

        print(f"Writing to {out_path}")
        plt.savefig(out_path)
        plt.clf()



def plotKeyData(key, name, data, *, limit=None):
    values = data[key].to_numpy()
    stats = getStats(values)

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
        if len(name) > 14:
            title = f"{key} Distribution\n{name}\n{title}"
        else:
            title = f"{key} Distribution - {name}\n{title}"

        plotHist(axs[i//2][i%2], title, values, line_value=line_value, limit=limit)

    ## Show
    #plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)


def plotHist(axs, title, values, limit=None, line_value=None):
    axs.hist(values, color='lightblue', ec='black', bins=15)
    axs.set_title(title)
    axs.set_xlabel("FAR")
    axs.set_ylabel("Number of Lots")
    min_ylim, max_ylim = axs.get_ylim()
    min_xlim, max_xlim = axs.get_xlim()
    txt_offset = max_xlim * 0.01
    line_data_sets = []
    if limit is not None:
        line_data_sets.append((limit, txt_offset, max_ylim*0.8, 'red', False))
    if line_value is not None:
        line_data_sets.append((line_value, txt_offset, max_ylim*0.5, 'darkblue'))

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
