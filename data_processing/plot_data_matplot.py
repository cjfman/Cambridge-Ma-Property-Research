#!/usr/bin/env python3.11

import os

# Import the geopandas and geoplot libraries
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gp

ROOT             = "/home/charles/Projects/cambridge_property_db/"
GEOJSON          = os.path.join(ROOT, "geojson")
blocks_path      = os.path.join(GEOJSON, "ADDRESS_MasterAddressBlocks.geojson")
block_stats_path = os.path.join(ROOT, "block_dimension_data.csv")

# Load the json file with coordinates
#geoData = gp.GeoDataFrame.from_file(('https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/US-counties.geojson')
geoData = gp.read_file('https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/US-counties.geojson')
geoData.plot()

