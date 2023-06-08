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


## Attempt to combine property sources
## Use main db as attoritative
missing_web = []
missing_gis = []
missing_building = []
for main_entry in main_db.entries:
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

    ## Convert to property
    prop = Property.fromJson(entry.toJson())

    ## Building
    if prop.building_id not in building_map:
        print(f"Property {prop.id} has no building. Couldn't find {prop.building_id}")
        missing_building.append(prop)
        continue

    building = building_map[prop.building_id]
    if prop.isBuilding():
        building.setMainProperty(prop)
    else:
        building.addProperty(prop)

data = {
    'buildings':        [x.toJson() for x in sorted(buildings, key=lambda x: x.id)],
    'rouge_properties': [x.toJson() for x in sorted(missing_building, key=lambda x: x.id)],
    'missing_web':      sorted(missing_web),
    'missing_gis':      sorted(missing_gis),
}
with open(out_path) as f:
    json.dump(data, f)
