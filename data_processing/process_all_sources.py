#!/usr/bin/python3

import json
import os

import progressbar

import data_sources as ds
import gis
from real_property import Property, Building

DO_GIS=True


## All file paths
ROOT         = "/home/charles/Projects/cambridge_property_db/"
DATA         = os.path.join(ROOT, "csvs")
GEOJSON      = os.path.join(ROOT, "geojson")
main_path    = os.path.join(DATA, "ASSESSING_PropertyDatabase_FY2023.csv")
#main_path    = os.path.join(DATA, "sigh.csv")
website_path = os.path.join(DATA, "properties.tsv")
master_path  = os.path.join(DATA, "ADDRESS_MasterAddressList.csv")
gis_path     = os.path.join(DATA, "gis_property_info.tsv")
out_path     = os.path.join(ROOT, "all_data.json")
zoning_path  = os.path.join(GEOJSON, "CDD_ZoningDistricts.geojson")
blocks_path  = os.path.join(GEOJSON, "ADDRESS_MasterAddressBlocks.geojson")


## Load all data sources
master_db  = ds.MasterDatabase(master_path,   verbose=True)
main_db    = ds.MainDatabase(main_path,       verbose=True)
website_db = ds.WebsiteDatabase(website_path, verbose=True)
gis_db     = ds.GisDatabase(gis_path,         verbose=True)
zones      = gis.ZoningDistricts(zoning_path)
blocks     = gis.CityBlocks(blocks_path)

## Create buildings
all_buildings = [Building.fromJson(x.toJson()) for x in master_db]
building_map = {}
for b in all_buildings:
    if b.id not in building_map:
        building_map[b.id] = b
    elif building_map[b.id].object_id != b.object_id:
        print(f"Found an alias for building {b.id}: {b.object_id}")
        building_map[b.id].addAlias(b)
    else:
        print(f"Dropping duplicate for building {b.id}: {b.object_id}")

buildings = building_map.values()


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
    building = None
    if entry.building_id in building_map:
        building = building_map[entry.building_id]
    elif entry.buildingIdFromMapLot() in building_map:
        building = building_map[entry.buildingIdFromMapLot()]
    else:
        print(f"Property {entry.id} has no building. Couldn't find {entry.building_id}")
        missing_building.append(entry)
        continue

    if entry.isBuilding():
        building.setMainEntry(entry)
    else:
        building.addProperty(Property.fromJson(entry.toJson()))


## Find zones and blocks
if DO_GIS:
    print("Searching GIS data for zoning district and city block")
    with progressbar.ProgressBar(max_value=len(buildings)) as bar:
        for i, b in enumerate(buildings):
            b.setZone(zones.findZone(b.location))
            b.setBlock(blocks.findBlock(b.location))
            bar.update(i)

## Final info
empty_buildings = tuple([x for x in buildings if not x.status()])
building_count = len(buildings)
all_building_count = len(all_buildings)
alias_count = all_building_count - building_count
print(f"Processed {count} properties and {building_count} buildings")
if alias_count:
    print(f"Found {alias_count} building address aliases")
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
