#!/usr/bin/python3

import json
import os

from collections import defaultdict, namedtuple
from statistics import mean, median, pstdev

import numpy as np

import gis

ROOT            = "/home/charles/Projects/cambridge_property_db/"
GEOJSON         = os.path.join(ROOT, "geojson")
STATS           = os.path.join(ROOT, "stats")
data_path       = os.path.join(ROOT, "all_data.json")
blocks_path     = os.path.join(GEOJSON, "ADDRESS_MasterAddressBlocks.geojson")
blocks_out_path = os.path.join(STATS, "all_percentile.csv")

Stats = namedtuple('Stats', ['mean', 'median', 'stddev', 'quantiles'])
ZONES_RES = ("A-1", "A-2", "B", "C", "C-1", "C-1A")
ZONES_INTS = ("C-3", "C-3A", "C-3B", "C-3", "C-3A", "C-3B")
ZONES_BIZ_LOW = ("BA", "BA-1", "BA-2", "BA-3", "BA-4", "BC", "O-1")
ZONES_BIZ_HIGH = ("BB", "BB-1", "BB-2", "O-2", "O-3", "C-2B") #, "O-2A", "O-3A", "MXD", "ASD")
ZONES_IND = ("IA", "IA-1" "IA-2", "IB", "IB-1", "IB-2", "IC")

FIRST_ST  = (483, 526, 547, 566, 571, 505, 468)
COURT     = (502, 479)
KENDAL    = (680,)
MID_MASS  = (524, 539, 493, 490, 501, 506)

ZONES     = []
NO_BLOCK  = [] #COURT
YES_BLOCK = []
MAX_FAR = 5.5


def main():
    raw_data = None
    with open(data_path) as f:
        raw_data = json.load(f)


    block_stats = calcBlockStats(raw_data, blocks_path)
    writeCsv(block_stats, blocks_out_path)


def getStats(data, res=2):
    stats = [round(x, res) for x in (mean(data), median(data), pstdev(data))]
    stats.append([round(x, res) for x in np.quantile(data, q=np.arange(.01, 1.00, .01))])
    #stats.append([round(x, res) for x in np.quantile(data, q=np.arange(.25, 1.00, .25))])
    return Stats(*stats)


def writeCsv(rows, path):
    with open(path, 'w') as f:
        for row in rows:
            f.write(",".join([str(x) for x in row]))
            f.write("\n")


def calcBlockStats(data, path):
    ## pylint: disable=too-many-locals
    block_gis = gis.CityBlocks(path)
    block_far  = defaultdict(list)
    block_ladu = defaultdict(list)
    block_os   = defaultdict(list)

    ## Go through each building and get the dimensions
    for b in data['buildings']:
        block = b['block']
        dim = b['dimensions']
        if not dim or dim['OPEN'] < 0:
            continue

        exclude = not block \
            or 'dimensions' not in b \
            or (ZONES and b['zone'] not in ZONES) \
            or dim['FAR'] > MAX_FAR

        if exclude and block not in YES_BLOCK:
            continue

        if block in NO_BLOCK:
            continue

        block_far[block].append(dim['FAR'])
        block_ladu[block].append(dim['LADU'])
        block_os[block].append(dim['OPEN'])

    ## Get the stats
    block_far_stats  = { key: getStats(val) for key, val in block_far.items() }
    block_ladu_stats = { key: getStats(val) for key, val in block_ladu.items() }
    block_os_stats   = { key: getStats(val) for key, val in block_os.items() }

    ## Produce the rows
    rows = []
    for block in block_far_stats.keys():
        geo_id     = block_gis.getGeoId(block)
        far_stats  = block_far_stats[block]
        ladu_stats = block_ladu_stats[block]
        os_stats   = block_os_stats[block]
        row = [
            geo_id,
            block,
            far_stats.mean,
            far_stats.median,
            far_stats.stddev,
            ladu_stats.mean,
            ladu_stats.median,
            ladu_stats.stddev,
            os_stats.mean,
            os_stats.median,
            os_stats.stddev,
        ]
        row += list(far_stats.quantiles)
        rows.append(row)

    rows.sort()
    columns = ['id', 'block',
        'far_mean',  'far_median',  'far_stddev',
        'ladu_mean', 'ladu_median', 'ladu_stddev',
        'os_mean',   'os_median',   'os_stddev',
    ]
    columns += [f"far_{x + 1}" for x in range(len(far_stats.quantiles))]
    rows = [columns] + rows

    return rows


def basicStats(data):
    zone_far  = defaultdict(list)
    zone_ladu = defaultdict(list)
    zone_os   = defaultdict(list)

    for b in data['buildings']:
        if not b['zone'] or 'dimensions' not in b:
            continue

        dim = b['dimensions']
        if not dim:
            continue

        zone = b['zone']
        zone_far[zone].append(dim['FAR'])
        zone_ladu[zone].append(dim['LADU'])
        zone_os[zone].append(dim['OPEN'])

    for zone in ('A-1', 'A-2', 'B', 'C', 'C-1', 'BA', 'BB', 'BC'):
        far        = round(mean(zone_far[zone]), 2)
        ladu       = round(mean(zone_ladu[zone]), 2)
        open_space = round(mean(zone_os[zone]), 2)
        far_stddev        = round(pstdev(zone_far[zone]), 2)
        ladu_stddev       = round(pstdev(zone_ladu[zone]), 2)
        open_space_stddev = round(pstdev(zone_os[zone]), 2)
        print(f"Mean Zone {zone} FAR:{far} LA/DU:{ladu} Open Space:{open_space}%")
        print(f"StdDev Zone {zone} FAR:{far_stddev} LA/DU:{ladu_stddev} Open Space:{open_space_stddev}%")

main()
