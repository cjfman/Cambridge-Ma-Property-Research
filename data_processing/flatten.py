#!/usr/bin/python3

import json
import os

import gis

import constants as cnts

ROOT      = "/home/charles/Projects/cambridge_property_db/"
GEOJSON   = os.path.join(ROOT, "geojson")
STATS     = os.path.join(ROOT, "stats")
lots_path = os.path.join(GEOJSON,"ASSESSING_ParcelsFY2023.geojson")
data_path = os.path.join(ROOT, "all_data.json")
out_path  = os.path.join(STATS, "lots_all.csv")
lot_gis   = gis.Lots(lots_path)


ZONES = None #cnts.ZONES_RES + cnts.ZONES_BIZ_LOW
NO_BLOCKS = cnts.FIRST_ST

js = None
with open(data_path) as f:
    js = json.load(f)

keys = (
    'street_name',
    'street_number',
    'zone',
    'block',
    'total_rooms',
    'bedrooms',
    'first_floor_area',
    'land_area',
    'living_area',
    'neighborhood',
    'num_stories',
    'property_class',
)
columns = ('id', 'ML') + keys + (
    'FAR',
    'LADU',
    'OPEN',
    'lot',
    'lat',
)

rows = [columns]
for b in js['buildings']:
    if ZONES and b['zone'] not in ZONES:
        continue

    if b['block'] in NO_BLOCKS:
        continue

    geo_id = lot_gis.getGeoId(b['id'])
    if geo_id is None:
        continue

    dim = b['dimensions']
    if not dim or dim['OPEN'] < 0:
        continue

    row = [geo_id, b['id']] + [b[key] for key in keys]
    row.append(dim['FAR'])
    row.append(dim['LADU'])
    row.append(dim['OPEN'])
    row.append(b['location'][0])
    row.append(b['location'][1])
    rows.append(row)


with open(out_path, 'w') as f:
    for row in rows:
        f.write(",".join([str(x) for x in row]))
        f.write("\n")
