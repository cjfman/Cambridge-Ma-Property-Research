from collections import defaultdict
from typing import Sequence


from data_sources import (
    MainDatabaseEntry,
    WebsiteDatabaseEntry,
    MasterListEntry,
    GisEntry,
)

class Property:
    ## pylint: disable=too-many-public-methods
    def __init__(self, *, main_entry=None, website_entry=None, gis_entry=None, **kwargs):
        kwargs = defaultdict(lambda: None, kwargs)
        self.main_entry: MainDatabaseEntry       = main_entry
        self.website_entry: WebsiteDatabaseEntry = website_entry
        self.gis_entry: GisEntry                 = gis_entry
        self._id               = kwargs['id']
        self._building_id      = kwargs['building_id']
        self._address          = kwargs['address']
        self._map_lot          = kwargs['map_lot']
        self._num_stories      = kwargs['num_stories']
        self._floor_location   = kwargs['floor_location']
        self._land_area        = kwargs['land_area']
        self._living_area      = kwargs['living_area']
        self._year_built       = kwargs['year_built']
        self._first_floor_area = kwargs['first_floor_area']

        if any(main_entry, website_entry, gis_entry):
            self._selfValidate()

    @classmethod
    def fromJson(cls, data):
        return cls(**data)

    @property
    def id(self):
        if self._id is not None:
            return self._id
        elif self.main_entry is not None:
            return self.main_entry.PropId

        raise Exception("No source for information found")

    @property
    def building_id(self):
        if self._building_id is not None:
            return self._building_id
        elif self.main_entry is not None:
            return self.main_entry.BldgNum

        raise Exception("No source for information found")

    @property
    def address(self):
        if self._address is not None:
            return self._address

        ## Preferibly use the text from the website
        if self.website_entry is not None:
            return self.website_entry.lblAddress

        ## Construct address from the main entry
        addr = self.main_entry.Address
        if self.main_entry.Unit is not None:
            addr += ' ' + self.main_entry.Unit

        return addr

    @property
    def map_lot(self):
        if self._map_lot is not None:
            return self._map_lot
        elif self.main_entry is not None:
            return self.main_entry.MapLot

        raise Exception("No source for information found")

    @property
    def num_stories(self):
        if self._num_stories is not None:
            return self._num_stories
        elif self.main_entry is not None:
            return self.main_entry.Exterior_NumStories

        raise Exception("No source for information found")

    @property
    def floor_location(self):
        if self._floor_location is not None:
            return self._floor_location
        elif self.main_entry is not None:
            return self.main_entry.Exterior_FloorLocation

        raise Exception("No source for information found")

    @property
    def land_area(self):
        if self._land_area is not None:
            return self._land_area
        elif self.gis_entry is not None:
            return self.gis_entry.LivingArea
        elif self.main_entry is not None:
            return self.main_entry.Interior_LivingArea

        raise Exception("No source for information found")

    @property
    def living_area(self):
        if self._living_area is not None:
            return self._living_area
        elif self.main_entry is not None:
            return self.main_entry.Interior_LivingArea

        raise Exception("No source for information found")

    @property
    def year_built(self):
        if self._year_built is not None:
            return self._year_built
        elif self.main_entry is not None:
            return self.main_entry.Condition_YearBuilt

        raise Exception("No source for information found")

    @property
    def first_floor_area(self):
        if self._first_floor_area is not None:
            return self._first_floor_area
        elif self.website_entry is not None:
            return self.website_entry.FirstFloor_GrossArea

        raise Exception("No source for information found")

    def setWebsiteEntry(self, website_entry:WebsiteDatabaseEntry):
        self.website_entry = website_entry
        self._selfValidate()

    def setGisEntry(self, gis_entry:GisEntry):
        self.gis_entry = gis_entry
        self._selfValidate()

    def isBuilding(self):
        return (self.main_entry.MapLot is None)

    def toBuilding(self):
        if not self.isBuilding():
            raise Exception("Cannot convert to building")

        return Building(main_entry=self.main_entry)

    def to_json(self):
        return {
            'id':               self.id,
            'building_id':      self.building_id,
            'address':          self.address,
            'map_lot':          self.map_lot,
            'num_stories':      self.num_stories,
            'floor_location':   self.floor_location,
            'land_area':        self.land_area,
            'living_area':      self.living_area,
            'year_built':       self.year_built,
            'first_floor_area': self.first_floor_area,
        }

    def _selfValidate(self):
        if self.website_entry is not None:
            ## Check property ID
            if self.main_entry.PID != self.website_entry.PropId:
                raise ValueError(f"Property IDs don't match. Found {self.main_entry.PID} and website {self.website_entry.PropId}")

            ## Check building ID
            if self.main_entry.MapLot != self.website_entry.MapLot:
                raise ValueError(f"Building IDs don't match. Found {self.main_entry.MapLot} and website {self.website_entry.MapLot}")

        if self.gis_entry is not None:
            ## Check property ID
            if self.main_entry.PID != self.gis_entry.PID:
                raise ValueError(f"Property IDs don't match. Found {self.main_entry.PID} and gis {self.gis_entry.PID}")

            ## Check building ID
            if self.main_entry.MapLot != self.gis_entry.PropertyID:
                raise ValueError(f"Building IDs don't match. Found {self.main_entry.MapLot} and gis {self.gis_entry.PropertyID}")


class Building:
    ## pylint: disable=too-many-public-methods
    def __init__(self, *, properties=None, main_entry=None, master_list_entry=None,
            gis_entry=None, **kwargs):
        kwargs = defaultdict(lambda: None, kwargs)
        self._properties:Sequence[Property]     = list(properties or [])
        self._main_entry:MainDatabaseEntry      = main_entry
        self._master_list_entry:MasterListEntry = master_list_entry
        self._gis_entry:GisEntry                = gis_entry
        self._id             = kwargs['id']
        self._pid            = kwargs['pid']
        self._gis_id         = kwargs['gis_id']
        self._zone           = kwargs['zone']
        self._land_area      = kwargs['land_area']
        self._living_area    = kwargs['living_area']
        self._num_stories    = kwargs['num_stories']
        self._floor_location = kwargs['floor_location']
        self._num_units      = kwargs['num_units']
        self._total_rooms    = kwargs['total_rooms']
        self._bedrooms       = kwargs['bedrooms']
        self._location       = kwargs['location']
        self._neighborhood   = kwargs['neighborhood']
        self._block          = kwargs['block']
        self._block_group    = kwargs['block_group']
        self._tract          = kwargs['tract']
        self._first_floor_area = kwargs['first_floor_gross_area']

    @classmethod
    def fromJson(cls, data):
        if 'properties' in data:
            data['properties'] = [Property.fromJson(x) for x in data['properties']]

        return cls(**data)

    @property
    def properties(self):
        return list(self._properties)

    def set_properties(self, properties):
        self._properties = list(properties)

    @property
    def main_entry(self):
        return self._main_entry

    def set_main_entry(self, main_entry):
        self._main_entry = main_entry

    @property
    def gis_entry(self):
        return self._gis_entry

    def set_gis_entry(self, gis_entry):
        self._gis_entry = gis_entry

    @property
    def master_list_entry(self):
        return self._master_list_entry

    def set_master_list_entry(self, master_entry):
        self._master_list_entry = master_entry

    ## For most properties, prefer the object member, otherwise use the backup source
    @property
    def id(self):
        if self._id is not None:
            return self._id
        elif self.main_entry is not None:
            return self.main_entry.MapLot

        raise Exception(f"No source for information found for 'id'")

    @property
    def pid(self):
        if self._pid is not None:
            return self._pid
        elif self.main_entry is not None:
            return self.main_entry.PID

        raise Exception(f"No source for information found for 'pid'")

    @property
    def gis_id(self):
        if self._gis_id is not None:
            return self._gis_id
        elif self.main_entry is not None:
            return self.main_entry.GISID

        raise Exception(f"No source for information found for 'gis_id'")

    @property
    def zone(self):
        if self._zone is not None:
            return self._zone
        elif self.main_entry is not None:
            return self.main_entry.Zoning

        raise Exception(f"No source for information found for 'zone'")

    @property
    def land_area(self):
        if self._land_area is not None:
            return self._land_area
        elif self.gis_entry is not None:
            return self.gis_entry.LandArea
        elif self.main_entry is not None:
            return self.main_entry.LandArea

        ## None of the backup sources has land area
        ## Look for one in the properties
        if self._properties:
            areas = [x.land_area for x in self._properties if x.land_area is not None]
            if areas:
                return areas[0]

            return None

        raise Exception(f"No source for information found for 'land_area'")

    @property
    def living_area(self):
        if self._living_area is not None:
            return self._living_area
        elif self.main_entry is not None:
            return self.main_entry.Interior_LivingArea

        ## Sum up living areas of the properties
        return sum([x.living_area for x in self._properties])

    @property
    def num_stories(self):
        if self._num_stories is not None:
            return self._num_stories
        elif self.main_entry is not None:
            return self.main_entry.Exterior_NumStories

        raise Exception("No source for information found for 'num_stories'")

    @property
    def floor_location(self):
        if self._floor_location is not None:
            return self._floor_location
        elif self.main_entry is not None:
            return self.main_entry.Exterior_FloorLocation

        raise Exception("No source for information found for 'floor_location'")

    @property
    def num_units(self):
        if self._num_units is not None:
            return self._num_units
        elif self.main_entry is not None:
            return self.main_entry.Interior_NumUnits

        return len(self._properties)

    @property
    def total_rooms(self):
        if self._total_rooms is not None:
            return self._total_rooms
        elif self.main_entry is not None:
            return self.main_entry.Interior_TotalRooms

        ## Sum up from properties
        return sum([x.total_rooms for x in self._properties])

    @property
    def bedrooms(self):
        if self._bedrooms is not None:
            return self._bedrooms
        elif self.main_entry is not None:
            return self.main_entry.Interior_Bedrooms

        ## Sum up from properties
        return sum([x.bedrooms for x in self._properties])

    @property
    def location(self):
        if self._location is not None:
            return self._location
        elif self.master_list_entry is not None:
            return (self.master_list_entry.lat, self.master_list_entry.lon)

        raise Exception(f"No source for information found for 'location'")

    @property
    def neighborhood(self):
        if self._neighborhood is not None:
            return self._neighborhood
        elif self.master_list_entry is not None:
            return self.master_list_entry.Neighborhood

        raise Exception(f"No source for information found for 'neighborhood'")

    @property
    def block(self):
        if self._block is not None:
            return self._block
        elif self.master_list_entry is not None:
            return self.master_list_entry.Block

        raise Exception(f"No source for information found for 'block'")

    @property
    def block_group(self):
        if self._block_group is not None:
            return self._block_group
        elif self.master_list_entry is not None:
            return self.master_list_entry.BLKGRP

        raise Exception(f"No source for information found for 'block_group'")

    @property
    def tract(self):
        if self._tract is not None:
            return self._tract
        elif self.master_list_entry is not None:
            return self.master_list_entry.Tract

        raise Exception(f"No source for information found for 'tract'")

    @property
    def first_floor_area(self):
        if self._first_floor_area is not None:
            return self._first_floor_area
        elif self._properties:
            return self._properties[0].first_floor_area

        raise Exception(f"No source for information found for 'first_floor_area'")


    def to_json(self):
        data = {
            'id':               self.id,
            'pid':              self.pid,
            'gis_id':           self.gis_id,
            'zone':             self.zone,
            'land_area':        self.land_area,
            'living_area':      self.living_area,
            'num_stories':      self.num_stories,
            'floor_location':   self.floor_location,
            'num_units':        self.num_units,
            'total_rooms':      self.total_rooms,
            'bedrooms':         self.bedrooms,
            'location':         self.location,
            'neighborhood':     self.neighborhood,
            'block':            self.block,
            'block_group':      self.block_group,
            'tract':            self.tract,
            'first_floor_area': self.first_floor_area,
        }
        if self._properties:
            data['properties'] = [x.to_json() for x in self._properties]

        return None
