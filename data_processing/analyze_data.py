#!/usr/bin/python3

import json
import os

from collections import defaultdict, namedtuple
from statistics import mean, median, pstdev

import gis

ROOT            = "/home/charles/Projects/cambridge_property_db/"
GEOJSON         = os.path.join(ROOT, "geojson")
data_path       = os.path.join(ROOT, "all_data.json")
blocks_path     = os.path.join(GEOJSON, "ADDRESS_MasterAddressBlocks.geojson")
blocks_out_path = os.path.join(ROOT, "block_dimension_data.csv")

Stats = namedtuple('Stats', ['mean', 'median', 'stddev'])


def main():
    raw_data = None
    with open(data_path) as f:
        raw_data = json.load(f)


    block_stats = calcBlockStats(raw_data, blocks_path)
    writeCsv(block_stats, blocks_out_path)


def getStats(data, res=2):
    return Stats(*[round(x, res) for x in (mean(data), median(data), pstdev(data))])


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
        if not b['block'] or 'dimensions' not in b:
            continue

        dim = b['dimensions']
        if not dim or dim['OPEN'] < 0:
            continue

        block = b['block']
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
        rows.append([
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
        ])

    rows.sort()
    rows = [['id', 'block',
        'far_mean',  'far_median',  'far_stddev',
        'ladu_mean', 'ladu_median', 'ladu_stddev',
        'os_mean',   'os_median',   'os_stddev',
    ]] + rows

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
