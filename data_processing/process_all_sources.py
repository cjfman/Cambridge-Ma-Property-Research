#!/usr/bin/python3

import json
import os

import data_sources as ds
from real_property import Property, Building


## All file paths
ROOT         = "/home/charles/Projects/cambridge_property_db/"
DATA         = os.path.join(ROOT, "csvs")
main_path    = os.path.join(DATA, "ASSESSING_PropertyDatabase_FY2023.csv")
#main_path    = os.path.join(DATA, "sigh.csv")
website_path = os.path.join(DATA, "properties.tsv")
master_path  = os.path.join(DATA, "ADDRESS_MasterAddressList.csv")
gis_path     = os.path.join(DATA, "gis_property_info.tsv")
out_path     = os.path.join(ROOT, "all_data.json")


## Load all data sources
master_db  = ds.MasterDatabase(master_path,   verbose=True)
main_db    = ds.MainDatabase(main_path,       verbose=True)
website_db = ds.WebsiteDatabase(website_path, verbose=True)
gis_db     = ds.GisDatabase(gis_path,         verbose=True)

## Create buildings
buildings = [Building.fromJson(x.toJson()) for x in master_db]
building_map = {x.id: x for x in buildings}
for b in buildings:
    if building_map[b.id].object_id != b.object_id:
        print(f"Found an alias for building {b.id}: {b.object_id}")
        building_map[b.id].addAlias(b)


## Attempt to combine property sources
## Use main db as attoritative
count = 0
missing_web = []
missing_gis = []
missing_building = []
for main_entry in main_db.entries:
    count += 1
    entry = ds.CombinedEntry(main_entry)
    print(f"Processing property {entry.id}: {entry.address}")

    ## Website
    if entry.id in website_db:
        entry.setWebsiteEntry(website_db[entry.id])
    else:
        print(f"Property {entry.id} missing website data")
        missing_web.append(entry.id)

    ## GID
    if entry.id in gis_db:
        entry.setGisEntry(gis_db[entry.id])
    else:
        print(f"Property {entry.id} missing GIS data")
        missing_gis.append(entry.id)


    ## Building
    if entry.building_id not in building_map:
        print(f"Property {entry.id} has no building. Couldn't find {entry.building_id}")
        missing_building.append(entry)
        continue

    building = building_map[entry.building_id]
    if entry.isBuilding():
        building.setMainEntry(entry)
    else:
        building.addProperty(Property.fromJson(entry.toJson()))

empty_buildings = tuple([x for x in buildings if not x.status()])

print(f"Processed {count} properties and {len(buildings)} buildings")
if missing_building:
    print(f"Missing building: {len(missing_building)}")
if missing_web:
    print(f"Missing web: {len(missing_web)}")
if missing_gis:
    print(f"Missing gis: {len(missing_gis)}")
if empty_buildings:
    print(f"Buildings without properties: {len(empty_buildings)}")

data = {
    'buildings':        [x.toJson() for x in sorted(buildings, key=lambda x: x.id)],
    'rouge_properties': [x.toJson() for x in sorted(missing_building, key=lambda x: x.id)],
    'missing_web':      sorted(missing_web),
    'missing_gis':      sorted(missing_gis),
}
print(f"Writing to {out_path}")
with open(out_path, 'w') as f:
    json.dump(data, f, sort_keys=True, indent=4)
