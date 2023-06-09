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
    def findZone(self, point):
        found = self.findFeature(point)
        if not found:
            return None

        return found['properties']['ZONE_TYPE']


class CityBlocks(GisGeoJson):
    def findBlock(self, point):
        found = self.findFeature(point)
        if not found:
            return None

        return found['properties']['UNQ_ID']
