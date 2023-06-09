#!/usr/bin/python3

import json
import os

from collections import defaultdict
from statistics import mean, median, pstdev

ROOT     = "/home/charles/Projects/cambridge_property_db/"
out_path = os.path.join(ROOT, "all_data.json")

data = None
with open(out_path) as f:
    data = json.load(f)

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
