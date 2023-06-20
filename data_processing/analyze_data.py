#!/usr/bin/python3

## pylint: disable=too-many-locals

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
zones_out_path  = os.path.join(STATS, "zones_all_percentile.csv")
zones_summary   = os.path.join(STATS, "zones_summary.csv")
zones_all_path  = os.path.join(STATS, "zones")
areas_out_path  = os.path.join(STATS, "neighborhood_all_percentile.csv")
areas_all_path  = os.path.join(STATS, "areas")
areas_summary   = os.path.join(STATS, "neighborhood_summary.csv")

ZONES_RES = ("A-1", "A-2", "B", "C", "C-1", "C-1A")
ZONES_INTS = ("C-3", "C-3A", "C-3B", "C-3", "C-3A", "C-3B")
ZONES_BIZ_LOW = ("BA", "BA-1", "BA-2", "BA-3", "BA-4", "BC", "O-1")
ZONES_BIZ_HIGH = ("BB", "BB-1", "BB-2", "O-2", "O-3", "C-2B")
ZONES_IND = ("IA", "IA-1" "IA-2", "IB", "IB-1", "IB-2", "IC")
ZONES_OTHER =  ("O-2A", "O-3A", "MXD", "ASD")
ALL_ZONES = ZONES_RES + ZONES_INTS + ZONES_BIZ_LOW + ZONES_BIZ_HIGH + ZONES_IND + ZONES_OTHER

FIRST_ST  = (483, 526, 547, 566, 571, 505, 468)
COURT     = (502, 479)
KENDAL    = (680,)
MID_MASS  = (524, 539, 493, 490, 501, 506)

ZONES     = []
NO_BLOCK  = COURT #+ FIRST_ST
YES_BLOCK = []
MAX_FAR = None

Stats = namedtuple('Stats', ['mean', 'median', 'max', 'min', 'stddev', 'quantiles'])


def main():
    raw_data = None
    with open(data_path) as f:
        raw_data = json.load(f)

    #block_stats = writeBlockStats(raw_data, blocks_path, blocks_out_path)
    #writeZoneStats(raw_data, zones_out_path)
    #writeZoneStats(raw_data, zones_summary, summary=True)
    #writeZoneBlocksStats(raw_data, blocks_path, zones_all_path)
    #writeAreaStats(raw_data, areas_out_path)
    #writeAreaStats(raw_data, areas_summary, summary=True)
    writeAreaBlocksStats(raw_data, blocks_path, areas_all_path)


def getStats(data, res=2, reverse=False):
    stats = [round(x, res) for x in (mean(data), median(data), max(data), min([x for x in data if x >= 0]), pstdev(data))]
    stats.append([round(x, res) for x in np.quantile(data, q=np.arange(.01, 1.00, .01))])

    stats = Stats(*stats)
    if reverse:
        stats.quantiles.sort(reverse=True)

    return stats


def writeCsv(rows, path):
    print(f"Writing file {path}")
    with open(path, 'w') as f:
        for row in rows:
            f.write(",".join([str(x) for x in row]))
            f.write("\n")


def makeBlockGisIdMap(data, block_gis):
    geo_id_map = {}
    for b in data['buildings']:
        block = b['block']
        geo_id_map[block] = block_gis.getGeoId(block)

    return geo_id_map


def calcBlockStats(data, *, zones=None, area=None):
    ## pylint: disable=too-many-locals
    block_far  = defaultdict(list)
    block_ladu = defaultdict(list)
    block_os   = defaultdict(list)
    zones      = zones or ZONES

    ## Go through each building and get the dimensions
    for b in data['buildings']:
        block = b['block']
        dim = b['dimensions']
        if not dim or dim['OPEN'] < 0:
            continue

        exclude = not block \
            or 'dimensions' not in b \
            or (zones and b['zone'] not in zones) \
            or (area and b['neighborhood'] != area) \
            or (MAX_FAR and dim['FAR'] > MAX_FAR)

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
    return (block_far_stats, block_ladu_stats, block_os_stats)


def writeBlockStats(data, block_gis, out_path, *, zones=None, area=None, geo_id_map=None):
    geo_id_map = geo_id_map or {}
    if isinstance(block_gis, str):
        block_gis = gis.CityBlocks(block_gis)
    elif not isinstance(block_gis, gis.CityBlocks):
        raise ValueError("Argument 'block_gis' must be either of type 'str' or 'gis.CityBlocks'. Found:" + type(block_gis))

    block_far_stats, block_ladu_stats, block_os_stats = calcBlockStats(data, zones=zones, area=area)
    ## Produce the rows
    rows = []
    for block in block_far_stats.keys():
        geo_id = None
        if block not in geo_id_map:
            geo_id_map[block] = block_gis.getGeoId(block)

        geo_id     = geo_id_map[block]
        far_stats  = block_far_stats[block]
        ladu_stats = block_ladu_stats[block]
        os_stats   = block_os_stats[block]
        row = [
            geo_id,
            block,
            far_stats.mean,
            far_stats.median,
            far_stats.max,
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
        'far_mean',  'far_median',  'far_max', 'far_stddev',
        'ladu_mean', 'ladu_median', 'ladu_stddev',
        'os_mean',   'os_median',   'os_stddev',
    ]
    if rows:
        columns += [f"far_{x + 1}"  for x in range(len(far_stats.quantiles))]

    rows = [columns] + rows
    writeCsv(rows, out_path)


def calcZoneStats(data):
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

    ## Get the stats
    far_stats  = { key: getStats(val) for key, val in zone_far.items() }
    ladu_stats = { key: getStats(val, reverse=True) for key, val in zone_ladu.items() }
    os_stats   = { key: getStats(val, reverse=True) for key, val in zone_os.items() }
    return (far_stats, ladu_stats, os_stats)


def calcAreaStats(data):
    area_far  = defaultdict(list)
    area_ladu = defaultdict(list)
    area_os   = defaultdict(list)

    for b in data['buildings']:
        if not b['neighborhood'] or 'dimensions' not in b:
            continue

        dim = b['dimensions']
        if not dim:
            continue

        area = b['neighborhood']
        area_far[area].append(dim['FAR'])
        area_ladu[area].append(dim['LADU'])
        area_os[area].append(dim['OPEN'])

    ## Get the stats
    far_stats  = { key: getStats(val) for key, val in area_far.items() }
    ladu_stats = { key: getStats(val, reverse=True) for key, val in area_ladu.items() }
    os_stats   = { key: getStats(val, reverse=True) for key, val in area_os.items() }
    return (far_stats, ladu_stats, os_stats)


def writeZoneStats(data, out_path, summary=True):
    writeCsv(makeKeyStatsRows('zone', *calcZoneStats(data), summary=summary), out_path)


def writeAreaStats(data, out_path, *, summary=False):
    writeCsv(makeKeyStatsRows('neighborhood', *calcAreaStats(data), summary=summary), out_path)


def makeKeyStatsRows(key, key_far_stats, key_ladu_stats, key_os_stats, *, summary=False):
    ## Produce the rows
    quantile_indices = [74, 79, 89]
    rows = []
    for far_key in key_far_stats.keys():
        far_stats  = key_far_stats[far_key]
        ladu_stats = key_ladu_stats[far_key]
        os_stats   = key_os_stats[far_key]
        row = [
            far_key,
            far_stats.min,
            far_stats.max,
            far_stats.mean,
            far_stats.median,
            far_stats.stddev,
            ladu_stats.min,
            ladu_stats.max,
            ladu_stats.mean,
            ladu_stats.median,
            ladu_stats.stddev,
            os_stats.min,
            os_stats.max,
            os_stats.mean,
            os_stats.median,
            os_stats.stddev,
        ]
        if summary:
            row += [far_stats.quantiles[x]  for x in quantile_indices]
            row += [ladu_stats.quantiles[x] for x in quantile_indices]
            row += [os_stats.quantiles[x]   for x in quantile_indices]
        else:
            row += list(far_stats.quantiles)

        rows.append(row)

    rows.sort()
    columns = [
        key,
        'far_min', 'far_max', 'far_mean','far_median', 'far_stddev',
        'ladu_min', 'ladu_max', 'ladu_mean','ladu_median', 'ladu_stddev',
        'os_min', 'os_max', 'os_mean','os_median', 'os_stddev',
    ]
    if summary:
        columns += [f"far_{x + 1}"  for x in quantile_indices]
        columns += [f"ladu_{x + 1}" for x in quantile_indices]
        columns += [f"os_{x + 1}"   for x in quantile_indices]
    else:
        columns += [f"far_{x + 1}" for x in range(len(far_stats.quantiles))]

    return [columns] + rows


def writeZoneBlocksStats(data, gis_path, out_path):
    block_gis = gis.CityBlocks(gis_path)
    geo_id_map = makeBlockGisIdMap(data, block_gis)
    for zone in ALL_ZONES:
        writeBlockStats(data, block_gis, os.path.join(out_path, f"zone_{zone}_blocks.csv"), zones=[zone], geo_id_map=geo_id_map)


def writeAreaBlocksStats(data, gis_path, out_path):
    block_gis = gis.CityBlocks(gis_path)
    geo_id_map = makeBlockGisIdMap(data, block_gis)
    areas = { x['neighborhood'] for x in data['buildings'] }
    for area in areas:
        clean = area.lower()
        for x in [' ', '/']:
            clean = clean.replace(x, '_')

        writeBlockStats(data, block_gis, os.path.join(out_path, f"neighborhood_{clean}_blocks.csv"), area=area, geo_id_map=geo_id_map)


main()
