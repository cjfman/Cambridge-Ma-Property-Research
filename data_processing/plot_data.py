#!/usr/bin/env python3

import os

import folium

ROOT        = "/home/charles/Projects/cambridge_property_db/"
GEOJSON     = os.path.join(ROOT, "geojson")
MAPS        = os.path.join(ROOT, "maps")
STATS       = os.path.join(ROOT, "stats")
blocks_path = os.path.join(GEOJSON, "ADDRESS_MasterAddressBlocks.geojson")
stats_path  = os.path.join(STATS, "blocks_commercial_bb_percentile.csv")
out_path    = os.path.join(MAPS, "blocks_commercial_bb_mean.html")

import pandas as pd

state_data = pd.read_csv(stats_path)
m = folium.Map(location=[42.378, -71.11], zoom_start=14)

folium.Choropleth(
    geo_data=blocks_path,
    name="choropleth",
    data=state_data,
    columns=["id", "far_mean"],
    key_on="feature.id",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="FAR Mean",
    #bins=9,
    bins=[round(i*6/9, 1) for i in range(8)] + [5.5],
    #bins=list(range(9)),
).add_to(m)

folium.LayerControl().add_to(m)
m.save(out_path)
print(f"Wrote to {out_path}")
