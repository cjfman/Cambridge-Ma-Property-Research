from collections import defaultdict

class Property:
    ## pylint: disable=too-many-public-methods
    def __init__(self, **kwargs):
        kwargs = defaultdict(lambda: None, kwargs)
        self.id               = kwargs['id']
        self.building_id      = kwargs['building_id']
        self.address          = kwargs['address']
        self.map_lot          = kwargs['map_lot']
        self.num_stories      = kwargs['num_stories']
        self.floor_location   = kwargs['floor_location']
        self.land_area        = kwargs['land_area']
        self.living_area      = kwargs['living_area']
        self.year_built       = kwargs['year_built']
        self.first_floor_area = kwargs['first_floor_area']

    @classmethod
    def fromJson(cls, data):
        return cls(**data)

    def isBuilding(self):
        return (self.map_lot is None or self.map_lot == self.building_id)

    def toBuilding(self):
        if not self.isBuilding():
            raise Exception("Cannot convert to building")

        return Building(main_property=self)

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
        self._aliases          = []
        if main_property:
            self.setMainProperty(main_property)

    @classmethod
    def fromJson(cls, data):
        if 'properties' in data:
            data['properties'] = [Property.fromJson(x) for x in data['properties']]

        return cls(**data)

    def setMainProperty(self, main_property):
        """Set values that come from being the main property"""
        if self.pid is not None:
            raise Exception(f"Cannot set main property twice: Already set as {self.pid}")

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

    def addAlias(self, alias):
        self._aliases.append(alias)

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
            'OK'              : bool(self.pid or self._properties),
        }
        if self._properties:
            data['properties'] = [x.to_json() for x in self._properties]
        if self._aliases:
            data['aliases'] = [x.to_json() for x in self._aliases]

        return data
