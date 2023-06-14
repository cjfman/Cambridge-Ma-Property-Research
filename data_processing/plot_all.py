#!/usr/bin/env python3

## pylint: disable=too-many-locals

import math
import os

import folium
import numpy as np
import pandas as pd

from branca.element import Template, MacroElement

import color_schemes as cs
import gis
from simplehtml import Element, LinearGradient, Text, TickMark

ROOT        = "/home/charles/Projects/cambridge_property_db/"
GEOJSON     = os.path.join(ROOT, "geojson")
MAPS        = os.path.join(ROOT, "maps")
STATS       = os.path.join(ROOT, "stats")
OVERWRITE   = False

color_bin_3_5 = [round(i*3/9, 1) for i in range(8)] + [3.5]
color_bin_5 = [round(i*3/9, 1) for i in range(8)] + [5]
color_bin_5_5 = [round(i*5/9, 1) for i in range(8)] + [5.5]
color_bin_8 = [round(i*6/9, 1) for i in range(8)] + [8.5]

default = {
    'color': 'RdYlBu',
    #'bins': color_bin_5,
    'geo_path': os.path.join(GEOJSON, "ADDRESS_MasterAddressBlocks.geojson"),
    'overwrite': True,
}

data_sets = [
    ## Lots
    {
        'name': "Residential Lots",
        'column': 'FAR',
        'data_path': os.path.join(STATS, "lots_residential.csv"),
        'out_path': os.path.join(MAPS, "lots_residential.html"),
        'geo_path': os.path.join(GEOJSON, "ASSESSING_ParcelsFY2023.geojson"),
        'bins': color_bin_5,
        'overwrite': False,
    },
    {
        'name': "Residential and BA Lots",
        'column': 'FAR',
        'data_path': os.path.join(STATS, "lots_low.csv"),
        'out_path': os.path.join(MAPS, "lots_low.html"),
        'geo_path': os.path.join(GEOJSON, "ASSESSING_ParcelsFY2023.geojson"),
        'bins': color_bin_5,
        'overwrite': False,
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

    ## All
    {
        'name': "All Mean",
        'column': 'far_mean',
        'legend': 'FAR Mean',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "all_mean.html"),
        'bins': color_bin_5_5,
    },
    {
        'name': "All 75th Percentile",
        'column': 'far_75',
        'legend': 'FAR 75th Percentile',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "all_75.html"),
        'bins': color_bin_5_5,
    },
    {
        'name': "All 80th Percentile",
        'column': 'far_80',
        'legend': 'FAR 80th Percentile',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "all_80.html"),
        'bins': color_bin_5_5,
    },
    {
        'name': "All 90th Percentile",
        'column': 'far_90',
        'legend': 'FAR 90th Percentile',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "all_90.html"),
        'bins': color_bin_5_5,
    },
    {
        'name': "All Max FAR",
        'column': 'far_max',
        'legend': 'FAR Max FAR',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "all_max.html"),
        'bins': color_bin_5_5,
    },
]

def main():
    template = None
    with open(os.path.join(ROOT, "templates/map.html")) as f:
        template = f.read()

    for data_set in data_sets:
        override = dict(default)
        override.update(data_set)
        overwrite = (OVERWRITE or override['overwrite'])
        if not overwrite and os.path.isfile(data_set['out_path']):
            continue

        #plotChoropleth(**override)
        plotGeoJson(template=template, **override)


def plotChoropleth(name, geo, out_path, data_path, column, color, legend=None, bins=None):
    print(f"Generating choropleth {name}")
    print(f"Reading {data_path}")
    data  = pd.read_csv(data_path)
    m      = folium.Map(location=[42.378, -71.11], zoom_start=14)
    legend = legend or column
    bins   = bins or 9
    folium.Choropleth(
        geo_data=geo,
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


def plotGeoJson(name, geo_path, out_path, data_path, column, template=None, **kwargs):
    print(f"Generating {name}")
    print(f"Reading {data_path}")
    data = pd.read_csv(data_path, index_col='id')
    values = data[column]

    print(f"Reading {geo_path}")
    geojson = gis.GisGeoJson(geo_path)
    gradient = cs.ColorGradient(cs.BlueRedYellow, 7, scale_fn=lambda x: math.log(1 + x))
    #gradient = cs.ColorGradient(cs.BlueRedYellow, int(values.max()), scale_fn=lambda x: math.log(1 + x))

    geojson.setProperty(column, "N/A")
    for i, row in data.iterrows():
        geojson.setProperty(column, row[column], i)

    ## Make style function
    style_function = lambda x: {
        'fillColor': gradient.pick(float(noThrow(values, x['id']) or 0) or None),
        'fillOpacity': 0.7,
        'weight': 2,
        'color': '#000000',
        'opacity': 0.2,
    }

    ## Make map
    m = folium.Map(location=[42.378, -71.11], zoom_start=14)
    geo = folium.GeoJson(geojson.geojson, name=name, style_function=style_function)
    folium.GeoJsonTooltip(fields=[column], aliases=['FAR'], sticky=False).add_to(geo)
    geo.add_to(m)
    folium.LayerControl(position='topleft', collapsed=False).add_to(m)

    ## Load template
    if template is not None:
        key_values = list(np.arange(gradient.min, 3, 0.5))
        key_values += list(np.arange(3, gradient.max, 1))
        key_values = [float(x) for x in key_values] + [gradient.max]
        color_key = makeColorKey(name, gradient, values=key_values)
        template = template.replace("{{SVG}}", color_key)
        macro = MacroElement()
        macro._template = Template(template) ## pylint: disable=protected-access
        m.get_root().add_child(macro)

    m.save(out_path)
    print(f"Wrote to {out_path}")


def noThrow(values, key):
    if key not in values:
        return None

    return values[key]


def htmlElemGen(tag, data='', **kwargs):
    attrs = " ".join([f'{k.replace("_", "-")}="{v}"' for k, v in kwargs.items()])
    return f'<{tag} {attrs}>{data}</{tag}>'


def makeColorKey(title, gradient, cbox_h=20, cbox_w=400, tick_h=10, values=None):
    values = values or []
    ## Add data
    color_tag = "color-scheme-red"
    gradient_el = LinearGradient(gradient, color_tag)

    ## Add elements
    y_off = 20
    x_off = 10
    text_h = 15
    els = []

    ## Title
    els.append(Text(title, x=x_off, y=y_off))
    y_off += text_h

    els.append(Text('FAR', x=x_off, y=y_off))
    y_off += text_h/2

    ## Create Color box
    els.append(Element('defs', gradient_el))
    els.append(Element(
        'rect', x=x_off, y=y_off, width=cbox_w, height=cbox_h,
        stroke='black', stroke_width=2,
        fill=f"url(#{color_tag})",
    ))
    y_off += cbox_h

    ## Create Ticks
    ticks = []
    for value in values:
        x = x_off + int(cbox_w*gradient.percent(value)/100)
        text_y = y_off + int(tick_h*1.1) + text_h
        ticks.append(TickMark(x=x, y=y_off, height=tick_h, width=2))
        if value < gradient.max:
            ticks.append(Text("%0.2g" % value, x=x, y=text_y))
        else:
            ticks.append(Text("%0.2g+" % value, x=x-10, y=text_y))
            break

    y_off += int(tick_h*1.1) + text_h
    els.append(Element('g', ticks))

    ## Create SVG
    width = cbox_w + 20
    height = y_off
    return Element('svg', els, width=width, height=height).to_html()


main()
