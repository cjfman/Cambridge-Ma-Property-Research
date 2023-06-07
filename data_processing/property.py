from collections import defaultdict

from data_sources import (
    MainDatabaseEntry,
    WebsiteDatabaseEntry,
    GisEntry,
)

class MissingDataError(Exception):
    def __init__(self, name):
        Exception.__init__(f"No source for information found for '{name}'")
        self.name = name


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

        raise MissingDataError('id')

    @property
    def building_id(self):
        if self._building_id is not None:
            return self._building_id
        elif self.main_entry is not None:
            return self.main_entry.getBuildingId()

        raise MissingDataError('building_id')

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

        raise MissingDataError('map_lot')

    @property
    def num_stories(self):
        if self._num_stories is not None:
            return self._num_stories
        elif self.main_entry is not None:
            return self.main_entry.Exterior_NumStories

        raise MissingDataError('num_stories')

    @property
    def floor_location(self):
        if self._floor_location is not None:
            return self._floor_location
        elif self.main_entry is not None:
            return self.main_entry.Exterior_FloorLocation

        raise MissingDataError('floor_location')

    @property
    def land_area(self):
        if self._land_area is not None:
            return self._land_area
        elif self.gis_entry is not None:
            return self.gis_entry.LandArea
        elif self.main_entry is not None:
            return self.main_entry.Interior_LandArea

        raise MissingDataError('land_area')

    @property
    def living_area(self):
        if self._living_area is not None:
            return self._living_area
        elif self.main_entry is not None:
            return self.main_entry.Interior_LivingArea

        raise MissingDataError('living_area')

    @property
    def year_built(self):
        if self._year_built is not None:
            return self._year_built
        elif self.main_entry is not None:
            return self.main_entry.Condition_YearBuilt

        raise MissingDataError('year_built')

    @property
    def first_floor_area(self):
        if self._first_floor_area is not None:
            return self._first_floor_area
        elif self.website_entry is not None:
            return self.website_entry.FirstFloor_GrossArea

        raise MissingDataError('first_floor_area')

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
        try:
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
                'OK': True,
            }
        except MissingDataError:
            return {
                'id':               self._id,
                'building_id':      self._building_id,
                'address':          self._address,
                'map_lot':          self._map_lot,
                'num_stories':      self._num_stories,
                'floor_location':   self._floor_location,
                'land_area':        self._land_area,
                'living_area':      self._living_area,
                'year_built':       self._year_built,
                'first_floor_area': self._first_floor_area,
                'OK': False,
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
    def __init__(self, *, main_property=None, properties=None, **kwargs):
        kwargs = defaultdict(lambda: None, kwargs)
        self.id                = kwargs['id']
        self.pid               = kwargs['pid']
        self.street_number     = kwargs['street_number']
        self.street_name       = kwargs['street_name']
        self.full_address      = kwargs['full_address']
        self.zipcode           = kwargs['zipcode']
        self._zone             = kwargs['zone']
        self._land_area        = kwargs['land_area']
        self._living_area      = kwargs['living_area']
        self.num_stories       = kwargs['num_stories']
        self.num_units         = kwargs['num_units']
        self._total_rooms      = kwargs['total_rooms']
        self._bedrooms         = kwargs['bedrooms']
        self.location          = kwargs['location']
        self.neighborhood      = kwargs['neighborhood']
        self.block             = kwargs['block']
        self.block_group       = kwargs['block_group']
        self.tract             = kwargs['tract']
        self._first_floor_area = kwargs['first_floor_area']
        self._properties       = list(properties or [])
        if main_property:
            self.setMainProperty(main_property)


    @classmethod
    def fromJson(cls, data):
        if 'properties' in data:
            data['properties'] = [Property.fromJson(x) for x in data['properties']]

        return cls(**data)

    def setMainProperty(self, main_property):
        """Set values that come from being the main property"""
        self.pid          = main_property.id
        self._zone        = main_property.zone
        self._land_area   = main_property.land_area
        self._living_area = main_property.land_area
        self.num_stories  = main_property.num_stories
        self.num_units    = main_property.num_units
        self._total_rooms = main_property.total_rooms
        self._bedrooms    = main_property.bedrooms

    def addProperty(self, new_property):
        self.properties.append(new_property)

    @property
    def properties(self):
        return list(self._properties)

    def set_properties(self, properties):
        self._properties = list(properties)

    ## For most properties, prefer the object member, otherwise use the backup source
    @property
    def zone(self):
        return self._zone

    @property
    def land_area(self):
        if self._land_area is not None:
            return self._land_area

        ## Look for one in the properties
        if self._properties:
            areas = [x.land_area for x in self._properties if x.land_area is not None]
            if areas:
                return areas[0]

        return None

    @property
    def living_area(self):
        if self._living_area is not None:
            return self._living_area

        ## Sum up living areas of the properties
        if self._properties:
            return sum([x.living_area for x in self._properties])

        return None

    @property
    def total_rooms(self):
        if self._total_rooms is not None:
            return self._total_rooms

        ## Sum up from properties
        if self._properties:
            return sum([x.total_rooms for x in self._properties])

        return None

    @property
    def bedrooms(self):
        if self._bedrooms is not None:
            return self._bedrooms

        ## Sum up from properties
        if self._properties:
            return sum([x.bedrooms for x in self._properties])

        return None

    @property
    def first_floor_area(self):
        if self._first_floor_area is not None:
            return self._first_floor_area
        elif self._properties:
            return self._properties[0].first_floor_area

        return None

    def to_json(self):
        data = {
            'id':               self.id,
            'pid':              self.pid,
            'street_number':    self.street_number,
            'street_name':      self.street_name,
            'zone':             self.zone,
            'land_area':        self.land_area,
            'living_area':      self.living_area,
            'num_stories':      self.num_stories,
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

        return data
