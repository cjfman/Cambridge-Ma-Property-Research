#!/usr/bin/env python3

## pylint: disable=too-many-locals

import json
import os

from collections import defaultdict

import constants as cnts

ROOT      = "/home/charles/Projects/cambridge_property_db/"
data_path = os.path.join(ROOT, "all_data.json")
out_path  = os.path.join(ROOT, "stats/non_conformance.csv")


def to_perc(val, total):
    return "%0.2f" % (val * 100 / total)


def format_perc(val, total):
    return f"{val} ({to_perc(val, total)}%)"


def main():
    data = None
    with open(data_path) as f:
        data = json.load(f)

    prop_zones = defaultdict(list)
    for b in data['buildings']:
        prop_zones[b['zone']].append(b)

    writeNonConformance(prop_zones)


def writeNonConformance(data):
    rows = [(
        'zone', 'total', 'nc_count', 'nc_far_count', 'nc_ladu_count', 'nc_oc_count',
        'nc_perc', 'nc_far_perc', 'nc_ladu_perc', 'nc_oc_perc',
    )]
    for zone in cnts.FAR_ZONES:
        rows.append(analyzeZone(zone, data[zone], pretty=False))

    writeCsv(rows, out_path)


def analyzeZonePretty(zone, data):
    limit_far = cnts.FAR_ZONES[zone]
    limit_ladu = cnts.LADU_ZONES[zone]
    limit_os   = cnts.OS_ZONES[zone]
    bad_count_far  = 0
    bad_count_ladu = 0
    bad_count_os   = 0
    bad_count_all  = 0
    for prop in data:
        bad = False
        dim = prop['dimensions']
        if not dim or dim['OPEN'] < 0:
            continue

        if dim['FAR'] > limit_far:
            bad_count_far += 1
            bad = True
        if dim['LADU'] < limit_ladu:
            bad_count_ladu += 1
            bad = True
        if limit_os and dim['OPEN'] < limit_os:
            bad_count_os += 1
            bad = True

        if bad:
            bad_count_all += 1

    total = len(data)
    print(f"Zone {zone} {total} lots. Non compliant {format_perc(bad_count_all, total)}")
    print(f"\tFAR {format_perc(bad_count_far, total)}")
    print(f"\tLADU {format_perc(bad_count_ladu, total)}")
    print(f"\tOS {format_perc(bad_count_os, total)}")


def analyzeZone(zone, data, *, pretty=False):
    limit_far = cnts.FAR_ZONES[zone]
    limit_ladu = cnts.LADU_ZONES[zone]
    limit_os   = cnts.OS_ZONES[zone]
    bad_count_far  = 0
    bad_count_ladu = 0
    bad_count_os   = 0
    bad_count_all  = 0
    for prop in data:
        bad = False
        dim = prop['dimensions']
        if not dim or dim['OPEN'] < 0:
            continue

        if dim['FAR'] > limit_far:
            bad_count_far += 1
            bad = True
        if dim['LADU'] < limit_ladu:
            bad_count_ladu += 1
            bad = True
        if limit_os and dim['OPEN'] < limit_os:
            bad_count_os += 1
            bad = True

        if bad:
            bad_count_all += 1

    total = len(data)
    if pretty:
        return (zone, total) + tuple([f"{x} ({round(x/total*100, 2)}%)" for x in (bad_count_all, bad_count_far, bad_count_ladu, bad_count_os)])

    return (zone, total, bad_count_all, bad_count_far, bad_count_ladu, bad_count_os) + tuple([round(x/total*100, 2) for x in (bad_count_all, bad_count_far, bad_count_ladu, bad_count_os)])


def writeCsv(rows, path):
    print(f"Writing file {path}")
    with open(path, 'w') as f:
        for row in rows:
            f.write(",".join([str(x) for x in row]))
            f.write("\n")

main()
