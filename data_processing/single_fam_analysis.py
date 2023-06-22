#!/usr/bin/env python3

## pylint: disable=too-many-locals

import json
import os

from collections import defaultdict

import constants as cnts
from prop_stats import getStats, statsSummary

ROOT      = "/home/charles/Projects/cambridge_property_db/"
data_path = os.path.join(ROOT, "all_data.json")
ZONES = ("A-1", "A-2", "B")

def main():
    data = None
    with open(data_path) as f:
        data = json.load(f)

    prop_zones = defaultdict(list)
    for b in data['buildings']:
        prop_zones[b['zone']].append(b)

    for zone in ZONES:
        analyzeZone(zone, prop_zones[zone])
        print()


def calcDimensionStats(data, dimension, *, reverse=False):
    return getStats([x['dimensions'][dimension] for x in data], reverse=reverse)


def to_perc(val, total):
    return "%0.2f" % (val * 100 / total)


def analyzeZone(zone, data):
    single_fams = []
    duplexes    = []
    multi_fams  = []
    other_res   = []
    other       = []
    total = len(data)
    far_bad_count  = 0
    far_bad_duplex = 0
    far_bad_multi  = 0
    for prop in data:
        dim = prop['dimensions']
        if not dim or dim['OPEN'] < 0:
            continue

        ## Categorize
        property_class = prop['property_class']
        if property_class in cnts.SNG_FAM_PROPERTY_CLASS:
            single_fams.append(prop)
        elif property_class in cnts.TWO_FAM_PROPERTY_CLASS:
            duplexes.append(prop)
        elif property_class in cnts.MULTI_FAM_PROPERTY_CLASS:
            multi_fams.append(prop)
        elif property_class in cnts.OTHER_RES_PROPERTY_CLASS:
            other_res.append(prop)
        else:
            other.append(prop)

        ## Check FAR
        if dim['FAR'] > cnts.FAR_ZONES[zone]:
            far_bad_count += 1
            if property_class in cnts.TWO_FAM_PROPERTY_CLASS:
                far_bad_duplex += 1
            elif property_class in cnts.MULTI_FAM_PROPERTY_CLASS:
                far_bad_multi += 1


    duplex_far_stats  = calcDimensionStats(duplexes, 'FAR')
    duplex_ladu_stats = calcDimensionStats(duplexes, 'LADU', reverse=True)
    duplex_os_stats   = calcDimensionStats(duplexes, 'OPEN', reverse=True)
    multi_fam_far_stats  = calcDimensionStats(multi_fams, 'FAR')
    multi_fam_ladu_stats = calcDimensionStats(multi_fams, 'LADU', reverse=True)
    multi_fam_os_stats   = calcDimensionStats(multi_fams, 'OPEN', reverse=True)

    print(f"Zone {zone}")
    print(f"Found {total} properties")
    print(f"Single families: {len(single_fams)} ({to_perc(len(single_fams), total)}%)")
    print(f"Duplexes: {len(duplexes)} ({to_perc(len(duplexes), total)}%)")
    print(f"\tFAR: ", statsSummary(duplex_far_stats))
    print(f"\tLA/DU: ", statsSummary(duplex_ladu_stats))
    print(f"\tOS: ", statsSummary(duplex_os_stats))
    print(f"Multi-Families: {len(multi_fams)} ({to_perc(len(multi_fams), total)}%)")
    print(f"\tFAR: ", statsSummary(multi_fam_far_stats))
    print(f"\tLA/DU: ", statsSummary(multi_fam_ladu_stats))
    print(f"\tOS: ", statsSummary(multi_fam_os_stats))
    print(f"All homes {far_bad_count} ({to_perc(far_bad_count, total)}%) FAR is too large")
    print(f"Duplexes {far_bad_duplex} ({to_perc(far_bad_duplex, len(duplexes))}%) FAR is too large")
    print(f"Multi Families {far_bad_multi} ({to_perc(far_bad_multi, len(multi_fams))}%) FAR is too large")



main()
