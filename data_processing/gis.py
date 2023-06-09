import json
from shapely.geometry import shape, Point

class GisGeoJson:
    def __init__(self, path):
        self.geojson = None
        with open(path) as f:
            self.geojson = json.load(f)

    def findAllFeatures(self, point):
        if not isinstance(point, Point):
            point = Point(point)

        found = []
        for feature in self.geojson['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                found.append(feature)

        return found

    def findFeature(self, point):
        found = self.findAllFeatures(point)
        if not found:
            return None

        return found[0]


class ZoningDistricts(GisGeoJson):
    def __init__(self, path):
        GisGeoJson.__init__(self, path)
        self.zone_to_id_map = {}
        self.id_to_zone_map = {}
        for feature in self.geojson['features']:
            zone = feature['properties']['ZONE_TYPE']
            geo_id = feature['id']
            self.zone_to_id_map[zone] = geo_id
            self.id_to_zone_map[geo_id] = zone

    def findZone(self, point):
        found = self.findFeature(point)
        if not found:
            return None

        return found['properties']['ZONE_TYPE']

    def getGeoId(self, zone):
        if zone not in self.zone_to_id_map:
            return None

        return self.zone_to_id_map[zone]


class CityBlocks(GisGeoJson):
    def __init__(self, path):
        GisGeoJson.__init__(self, path)
        self.block_to_id_map = {}
        self.id_to_block_map = {}
        for feature in self.geojson['features']:
            block_id = feature['properties']['UNQ_ID']
            geo_id = feature['id']
            self.block_to_id_map[block_id] = geo_id
            self.id_to_block_map[geo_id] = block_id


    def findBlock(self, point):
        found = self.findFeature(point)
        if not found:
            return None

        return found['properties']['UNQ_ID']

    def getGeoId(self, block):
        if block not in self.block_to_id_map:
            return None

        return self.block_to_id_map[block]
