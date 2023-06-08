from collections import defaultdict

class Property:
    ## pylint: disable=too-many-public-methods
    def __init__(self, **kwargs):
        kwargs = defaultdict(lambda: None, kwargs)
        self.id               = kwargs['id']
        self.address          = kwargs['address']
        self.property_class   = kwargs['property_class']
        self.map_lot          = kwargs['map_lot']
        self.num_stories      = kwargs['num_stories']
        self.floor_location   = kwargs['floor_location']
        self.land_area        = kwargs['land_area']
        self.living_area      = kwargs['living_area']
        self.year_built       = kwargs['year_built']
        self.total_rooms      = kwargs['total_rooms']
        self.bedrooms         = kwargs['bedrooms']
        self.first_floor_area = kwargs['first_floor_area']

    @classmethod
    def fromJson(cls, data):
        return cls(**data)

    def toJson(self):
        return {
            'id':               self.id,
            'address':          self.address,
            'property_class':   self.property_class,
            'map_lot':          self.map_lot,
            'num_stories':      self.num_stories,
            'floor_location':   self.floor_location,
            'land_area':        self.land_area,
            'living_area':      self.living_area,
            'year_built':       self.year_built,
            'total_rooms':      self.total_rooms,
            'bedrooms':         self.bedrooms,
            'first_floor_area': self.first_floor_area,
        }


class Building:
    ## pylint: disable=too-many-public-methods
    def __init__(self, *, main_entry=None, properties=None, **kwargs):
        kwargs = defaultdict(lambda: None, kwargs)
        self.id                = kwargs['id']
        self.pid               = kwargs['pid']
        self.object_id         = kwargs['object_id']
        self.street_number     = kwargs['street_number']
        self.street_name       = kwargs['street_name']
        self.full_address      = kwargs['full_address']
        self.zipcode           = kwargs['zipcode']
        self.property_class    = kwargs['property_class']
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
        if main_entry:
            self.setMainEntry(main_entry)

    @classmethod
    def fromJson(cls, data):
        if 'properties' in data:
            data['properties'] = [Property.fromJson(x) for x in data['properties']]

        return cls(**data)

    def setMainEntry(self, main_entry):
        """Set values that come from being the main entry"""
        if self.pid is not None:
            raise Exception(f"Cannot set main entry twice: Already set as {self.pid}")

        self.pid            = main_entry.id
        self.property_class = main_entry.property_class
        self._zone          = main_entry.zone
        self._land_area     = main_entry.land_area
        self._living_area   = main_entry.living_area
        self.num_stories    = main_entry.num_stories
        self.num_units      = main_entry.num_units
        self._total_rooms   = main_entry.total_rooms
        self._bedrooms      = main_entry.bedrooms

    def addProperty(self, new_property):
        self._properties.append(new_property)

    def addAlias(self, alias):
        self._aliases.append(alias)

    @property
    def properties(self):
        return tuple(self._properties)

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
            return sum([x.total_rooms or 0 for x in self._properties])

        return None

    @property
    def bedrooms(self):
        if self._bedrooms is not None:
            return self._bedrooms

        ## Sum up from properties
        if self._properties:
            return sum([x.bedrooms or 0 for x in self._properties])

        return None

    @property
    def first_floor_area(self):
        if self._first_floor_area is not None:
            return self._first_floor_area
        elif self._properties:
            return self._properties[0].first_floor_area

        return None

    def toJson(self):
        data = {
            'id':               self.id,
            'pid':              self.pid,
            'property_class':   self.property_class,
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
            data['properties'] = [x.toJson() for x in self._properties]
        if self._aliases:
            data['aliases'] = [x.toJson() for x in self._aliases]

        return data
