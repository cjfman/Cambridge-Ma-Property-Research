#!/usr/bin/env python3

## pylint: disable=too-many-locals

import math
import os

import folium
import numpy as np
import pandas as pd

from branca.element import Template, MacroElement

import color_schemes as cs
import constants as cnst
import gis
from simplehtml import Element, LinearGradient, Text, TickMark

ROOT        = "/home/charles/Projects/cambridge_property_db/"
GEOJSON     = os.path.join(ROOT, "geojson")
MAPS        = os.path.join(ROOT, "maps")
STATS       = os.path.join(ROOT, "stats")
OVERWRITE   = True

ZONES = cnst.ZONES_RES + ("BA", "BA-1", "BA-2", "BB", "BC")
DEFAULT = {
    'geo_path': os.path.join(GEOJSON, "ADDRESS_MasterAddressBlocks.geojson"),
    'overwrite': True,
    'skip': False,
}

FAR_DATA_SETS = [
    {
        'name': "Residential Lots",
        'column': 'FAR',
        'data_path': os.path.join(STATS, "lots_residential.csv"),
        'out_path': os.path.join(MAPS, "city_wide/property_lots_residential.html"),
        'geo_path': os.path.join(GEOJSON, "ASSESSING_ParcelsFY2023.geojson"),
        'overwrite': False,
    },
    {
        'name': "Lots",
        'column': 'FAR',
        'data_path': os.path.join(STATS, "lots_all.csv"),
        'out_path': os.path.join(MAPS, "city_wide/property_lots.html"),
        'geo_path': os.path.join(GEOJSON, "ASSESSING_ParcelsFY2023.geojson"),
        'overwrite': True,
    },
    {
        'title': "Mean FAR per Block",
        'name': 'Mean',
        'column': 'far_mean',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "city_wide/city_wide_mean.html"),
    },
    {
        'title': "Median FAR per Block",
        'name': "Median",
        'column': 'far_median',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "city_wide/city_wide_median.html"),
    },
    {
        'Title': "FAR 75th Percentile (1 of every 4)",
        'name': "75th Percentile",
        'column': 'far_75',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "city_wide/city_wide_75.html"),
    },
    {
        'title': "FAR 80th Percentile (1 of every 5)",
        'name': "80th Percentile",
        'column': 'far_80',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "city_wide/city_wide_80.html"),
    },
    {
        'title': "FAR 90th Percentile (1 of every 10)",
        'name': "90th Percentile",
        'column': 'far_90',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "city_wide/city_wide_90.html"),
    },
    {
        'title': "Max FAR on the Block",
        'name': "Max FAR on the Block",
        'column': 'far_max',
        'data_path': os.path.join(STATS, "all_percentile.csv"),
        'out_path': os.path.join(MAPS, "city_wide/city_wide_max.html"),
    },
]


ADDITIONAL_LAYERS = [
    {
        'name': "City Boundary",
        'geo_path': os.path.join(GEOJSON, "BOUNDARY_CityBoundary.geojson"),
        'show': True,
        'weight': 5,
    },
    {
        'name': "Zoning Districts",
        'geo_path': os.path.join(GEOJSON, "CDD_ZoningDistricts.geojson"),
        'tooltip': "ZONE_TYPE",
        'tooltip_name': "ZONE",
    },
    {
        'name': "Neighborhoods",
        'geo_path': os.path.join(GEOJSON, "BOUNDARY_CDDNeighborhoods.geojson"),
        'weight': 5,
        'tooltip': "NAME",
    },
]


def cleanTitle(title):
    for x in [' ', '/']:
        title = title.replace(x, '_')

    return title

def main():
    plotAll()
    #plotZones()
    #plotAreas()


def plotAll():
    template = None
    with open(os.path.join(ROOT, "templates/map.html")) as f:
        template = f.read()

    for data_set in FAR_DATA_SETS:
        override = dict(DEFAULT)
        override.update(data_set)
        overwrite = (OVERWRITE or override['overwrite'])
        if not overwrite and os.path.isfile(data_set['out_path']):
            continue
        if override['skip']:
            continue

        plotGeoJson(template=template, **override)


def plotZones():
    plotKeySections('Zone', 'zone', ZONES, 'zones')


def plotAreas():
    plotKeySections('Neighborhood', 'neighborhood', cnst.NEIGHBORHOODS, 'areas')


def plotKeySections(title, key, sections, prefix):
    template = None
    with open(os.path.join(ROOT, "templates/map.html")) as f:
        template = f.read()

    columns = {
        'far_mean':   "Mean",
        'far_median': "Median",
        'far_75':     "75th Percentile",
        'far_80':     "80th Percentile",
        'far_90':     "90th Percentile",
        'far_max':    "Max",
    }

    for section in sections:
        clean = cleanTitle(section)
        data_set = dict(DEFAULT)
        for column, name in columns.items():
            data_set.update({
                'name': f"{title} {section} {name}",
                'column': column,
                'data_path': os.path.join(STATS, f"{prefix}/{key}_{clean}_blocks.csv"),
                'out_path': os.path.join(MAPS, f"{prefix}/{key}_{clean}_{column}.html"),
            })

            overwrite = (OVERWRITE or data_set['overwrite'])
            if not overwrite and os.path.isfile(data_set['out_path']):
                continue

            plotGeoJson(template=template, **data_set)



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

    ## Plot extra layers
    for layer_def in ADDITIONAL_LAYERS:
        layer = makeLayer(**layer_def)
        layer.add_to(m)

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


def makeLayer(name, geo_path, show=False, weight=2, tooltip=None, tooltip_name=None, **kwargs):
    geojson = gis.GisGeoJson(geo_path)
    style_function = lambda x: {
        'fillColor': '#000000',
        'fillOpacity': 0.0,
        'weight': weight,
        'color': '#000000',
        'opacity': 1,
    }

    geo = folium.GeoJson(geojson.geojson, name=name, show=show, control=True, style_function=style_function)
    if tooltip is not None:
        tooltip_name = tooltip_name or tooltip
        folium.GeoJsonTooltip(fields=[tooltip], aliases=[tooltip], sticky=False).add_to(geo)

    return geo


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
