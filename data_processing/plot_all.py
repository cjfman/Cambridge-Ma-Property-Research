#!/usr/bin/env python3

import os

import folium
import pandas as pd

ROOT        = "/home/charles/Projects/cambridge_property_db/"
GEOJSON     = os.path.join(ROOT, "geojson")
MAPS        = os.path.join(ROOT, "maps_all")
STATS       = os.path.join(ROOT, "stats")
OVERWRITE   = False

color_bin_3_5 = [round(i*3/9, 1) for i in range(8)] + [3.5]
color_bin_5 = [round(i*3/9, 1) for i in range(8)] + [5]
color_bin_5_5 = [round(i*3/9, 1) for i in range(8)] + [5_5]

default = {
    'color': 'YlGnBu',
    'bins': color_bin_5,
    'geo_path': os.path.join(GEOJSON, "ADDRESS_MasterAddressBlocks.geojson"),
}

data_sets = [
    ## Lots
    {
        'name': "Residential Lots",
        'column': 'FAR',
        'data_path': os.path.join(STATS, "lots_residential.csv"),
        'out_path': os.path.join(MAPS, "lots_residential.html"),
        'geo_path': os.path.join(GEOJSON, "ASSESSING_ParcelsFY2023.geojson"),
    },
    {
        'name': "Residential and BA Lots",
        'column': 'FAR',
        'data_path': os.path.join(STATS, "lots_low.csv"),
        'out_path': os.path.join(MAPS, "lots_low.html"),
        'geo_path': os.path.join(GEOJSON, "ASSESSING_ParcelsFY2023.geojson"),
    },

    ## Residential
    {
        'name': "Residential Blocks Mean",
        'column': 'far_mean',
        'data_path': os.path.join(STATS, "blocks_residential_percentile.csv"),
        'out_path': os.path.join(MAPS, "blocks_residential_mean.html"),
        'bins': color_bin_3_5,
    },
    {
        'name': "Residential Blocks 75th Percentile",
        'column': 'far_75',
        'legend': 'FAR 75th Percentile',
        'data_path': os.path.join(STATS, "blocks_residential_percentile.csv"),
        'out_path': os.path.join(MAPS, "blocks_residential_75.html"),
        'bins': color_bin_3_5,
    },
    {
        'name': "Residential Blocks 90th Percentile",
        'column': 'far_90',
        'legend': 'FAR 90th Percentile',
        'data_path': os.path.join(STATS, "blocks_residential_percentile.csv"),
        'out_path': os.path.join(MAPS, "blocks_residential_90.html"),
        'bins': color_bin_3_5,
    },

    ## Commercial BA
    {
        'name': "Commercial BA Blocks Mean",
        'column': 'far_mean',
        'legend': 'FAR Mean',
        'data_path': os.path.join(STATS, "blocks_commercial_ba_percentile.csv"),
        'out_path': os.path.join(MAPS, "blocks_commercial_ba_mean.html"),
        'bins': color_bin_3_5,
    },
    {
        'name': "Commercial BA Blocks 75th Percentile",
        'column': 'far_75',
        'legend': 'FAR 75th Percentile',
        'data_path': os.path.join(STATS, "blocks_commercial_ba_percentile.csv"),
        'out_path': os.path.join(MAPS, "blocks_commercial_ba_75.html"),
        'bins': color_bin_3_5,
    },
    {
        'name': "Commercial BA Blocks 90th Percentile",
        'column': 'far_90',
        'legend': 'FAR 90th Percentile',
        'data_path': os.path.join(STATS, "blocks_commercial_ba_percentile.csv"),
        'out_path': os.path.join(MAPS, "blocks_commercial_ba_90.html"),
        'bins': color_bin_3_5,
    },

    ## Commercial BB
    {
        'name': "Commercial BB Blocks Mean",
        'column': 'far_mean',
        'legend': 'FAR Mean',
        'data_path': os.path.join(STATS, "blocks_commercial_bb_percentile.csv"),
        'out_path': os.path.join(MAPS, "blocks_commercial_bb_mean.html"),
        'bins': color_bin_5_5,
    },
    {
        'name': "Commercial BB Blocks 75th Percentile",
        'column': 'far_75',
        'legend': 'FAR 75th Percentile',
        'data_path': os.path.join(STATS, "blocks_commercial_bb_percentile.csv"),
        'out_path': os.path.join(MAPS, "blocks_commercial_bb_75.html"),
        'bins': color_bin_5_5,
    },
    {
        'name': "Commercial BB Blocks 90th Percentile",
        'column': 'far_90',
        'legend': 'FAR 90th Percentile',
        'data_path': os.path.join(STATS, "blocks_commercial_bb_percentile.csv"),
        'out_path': os.path.join(MAPS, "blocks_commercial_bb_90.html"),
        'bins': color_bin_5_5,
    },
]

def main():
    for data_set in data_sets:
        if not OVERWRITE and os.path.isfile(data_set['out_path']):
            continue

        override = dict(default)
        override.update(data_set)
        plotChart(**override)


def plotChart(name, geo_path, out_path, data_path, column, color, legend=None, bins=None):
    print(f"Generating {name}")
    print(f"Reading {data_path}")
    data  = pd.read_csv(data_path)
    m      = folium.Map(location=[42.378, -71.11], zoom_start=14)
    legend = legend or column
    bins   = bins or 9
    folium.Choropleth(
        geo_data=geo_path,
        name=name,
        data=data,
        columns=["id", column],
        key_on="feature.id",
        fill_color=color,
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend,
        bins=bins,
    ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(out_path)
    print(f"Wrote to {out_path}")


main()
