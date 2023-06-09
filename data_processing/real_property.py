from collections import defaultdict

class Namespace:
    def __init__(self, **kwargs):
        self.attrs = dict(kwargs or {}) ## Copy
        for attr, val in self.attrs.items():
            setattr(self, attr, val)

    def toJson(self):
        return dict(self.attrs)

class Property:
    ## pylint: disable=too-many-public-methods
    def __init__(self, **kwargs):
        kwargs = defaultdict(lambda: None, kwargs)
        self.id               = kwargs['id']
        self.address          = kwargs['address']
        self.unit             = kwargs['unit']
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
            'unit':             self.unit,
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
        self.address           = kwargs['address']
        self.street_number     = kwargs['street_number']
        self.street_name       = kwargs['street_name']
        self.full_address      = kwargs['full_address']
        self.zipcode           = kwargs['zipcode']
        self.property_class    = kwargs['property_class']
        self.zone              = kwargs['zone']
        self.block             = kwargs['block']
        self._land_area        = kwargs['land_area']
        self._living_area      = kwargs['living_area']
        self.num_stories       = kwargs['num_stories']
        self._num_units        = kwargs['num_units']
        self._total_rooms      = kwargs['total_rooms']
        self._bedrooms         = kwargs['bedrooms']
        self.location          = kwargs['location']
        self.neighborhood      = kwargs['neighborhood']
        self.block             = kwargs['block']
        self._first_floor_area = kwargs['first_floor_area']
        self._properties       = list(properties or [])
        self._aliases          = []
        self._duplicates       = []
        self._conflicts        = {}
        self._cache            = {}
        if main_entry:
            self.setMainEntry(main_entry)

    @classmethod
    def fromJson(cls, data):
        if 'properties' in data:
            data['properties'] = [Property.fromJson(x) for x in data['properties']]
        if 'aliases' in data:
            data['aliases'] = Namespace(**data['aliases'])
        if 'duplicates' in data:
            data['duplicates'] = Namespace(**data['duplicates'])

        return cls(**data)

    def setMainEntry(self, main_entry):
        """Set values that come from being the main entry"""
        if self.pid is not None:
            self._duplicates.append(main_entry)
            return

        self.pid            = main_entry.id
        self.property_class = main_entry.property_class
        self.address        = main_entry.address
        #self._zone          = main_entry.zone
        self._land_area     = main_entry.land_area
        self._living_area   = main_entry.living_area
        self.num_stories    = main_entry.num_stories
        self._num_units     = main_entry.num_units
        self._total_rooms   = main_entry.total_rooms
        self._bedrooms      = main_entry.bedrooms
        self._first_floor_area = main_entry.first_floor_area

    def addProperty(self, new_property):
        self._properties.append(new_property)

    def addAlias(self, alias):
        self._aliases.append(alias)

    def firstFloorProperties(self):
        return tuple(filter(lambda x: x.floor_location == 1, self._properties))

    def status(self):
        return bool(self.pid or self._properties)

    def setZone(self, zone):
        ## Set and mark confict if it's different
        if self.zone is not None and self.zone != zone:
            self._conflicts['zone'] = self.zone
        elif self.zone is None:
            self.zone = zone

    def setBlock(self, block):
        self.block = block

    def calculateDimensions(self):
        try:
            return {
                'FAR':  round(self.living_area / self.land_area, 2),
                'LADU': round(self.land_area / self.num_units, 2),
                'OPEN': round(self.open_area * 100 / self.land_area, 2),
            }
        except:
            return None

    @property
    def properties(self):
        return tuple(self._properties)

    def set_properties(self, properties):
        self._properties = list(properties)

    ## For most properties, prefer the object member, otherwise use the backup source
    @property
    def land_area(self):
        if 'land_area' in self._cache:
            return self._cache['land_area']

        ## Look for one in the properties
        if self._properties:
            areas = [x.land_area for x in self._properties if x.land_area is not None]
            if areas:
                ## Cache result and mark conflict if it's different
                area = areas[0]
                self._cache['land_area'] = area
                if self._land_area and self._land_area != area:
                    self._land_area = area
                    self._conflicts['land_area'] = area

        return self._land_area

    @property
    def open_area(self):
        return self.land_area - self.first_floor_area

    @property
    def living_area(self):
        if 'living_area' in self._cache:
            return self._cache['living_area']

        ## Sum up living areas of the properties
        if self._properties:
            living_area = sum([x.living_area for x in self._properties])
            if self._living_area != living_area:
                ## Mark conflict
                if self._living_area:
                    self._conflicts['living_area'] = self._living_area

                self._living_area = living_area

            ## Cache result
            self._cache['living_area'] = self._living_area

        return self._living_area

    @property
    def num_units(self):
        if self._num_units:
            return self._num_units

        return len(self._properties)

    @property
    def total_rooms(self):
        if 'total_rooms' in self._cache:
            return self._cache['total_rooms']

        ## Sum up toal rooms of the properties
        if self._properties:
            total_rooms = sum([x.total_rooms or 0 for x in self._properties])
            if self._total_rooms != total_rooms:
                ## Mark conflict
                if self._total_rooms:
                    self._conflicts['total_rooms'] = self._total_rooms

                self._total_rooms = total_rooms

            ## Cache result
            self._cache['total_rooms'] = total_rooms

        return self._total_rooms

    @property
    def bedrooms(self):
        if 'bedrooms' in self._cache:
            return self._cache['bedrooms']

        ## Sum up bedrooms of the properties
        if self._properties:
            bedrooms = sum([x.bedrooms or 0 for x in self._properties])
            ## Mark conflict
            if self._bedrooms != bedrooms:
                if self._bedrooms:
                    self._conflicts['bedrooms'] = self._bedrooms

                self._bedrooms = bedrooms

            ## Cache result
            self._cache['bedrooms'] = bedrooms

        return self._bedrooms

    @property
    def first_floor_area(self):
        if self._properties:
            return sum([x.first_floor_area or 0 for x in self.firstFloorProperties()])

        return self._first_floor_area

    def toJson(self):
        data = {
            'id':               self.id,
            'pid':              self.pid,
            'property_class':   self.property_class,
            'address':          self.address,
            'street_number':    self.street_number,
            'street_name':      self.street_name,
            'zone':             self.zone,
            'block':            self.block,
            'land_area':        self.land_area,
            'living_area':      self.living_area,
            'num_stories':      self.num_stories,
            'num_units':        self.num_units,
            'total_rooms':      self.total_rooms,
            'bedrooms':         self.bedrooms,
            'location':         self.location,
            'neighborhood':     self.neighborhood,
            'first_floor_area': self.first_floor_area,
            'dimensions':       self.calculateDimensions(),
            'OK'              : self.status(),
        }
        if self._properties:
            data['properties'] = [x.toJson() for x in self._properties]
        if self._aliases:
            data['aliases'] = [x.toJson() for x in self._aliases]
        if self._duplicates:
            data['duplicates'] = [x.toJson() for x in self._duplicates]
        if self._conflicts:
            data['conflicts'] = self._conflicts

        return data
