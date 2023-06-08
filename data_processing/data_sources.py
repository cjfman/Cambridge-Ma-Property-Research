import csv

from collections import defaultdict

MAIN_COLUMNS = (
    'PID',
    'GISID',
    'BldgNum',
    'Address',
    'Unit',
    'PropertyClass',
    'Zoning',
    'MapLot',
    'LandArea',
    'Owner_Name',
    'Owner_CoOwnerName',
    'Owner_Address',
    'Owner_Address2',
    'Owner_City',
    'Owner_State',
    'Owner_Zip',
    'Exterior_Style',
    'Exterior_Occupancy',
    'Exterior_NumStories',
    'Exterior_FloorLocation',
    'Exterior_View',
    'Interior_LivingArea',
    'Interior_NumUnits',
    'Interior_TotalRooms',
    'Interior_Bedrooms',
    'Condition_YearBuilt',
    'Condition_InteriorCondition',
    'Condition_OverallCondition',
    'Condition_OverallGrade',
)

MAIN_INT_COLUMNS = (
    'PID',
    'BldgNum',
    'LandArea',
    'Exterior_FloorLocation',
    'Interior_LivingArea',
    'Interior_NumUnits',
    'Interior_TotalRooms',
    'Interior_Bedrooms',
    'Condition_YearBuilt',
)

MAIN_FLOAT_COLUMNS = (
    'Exterior_NumStories',
)

WEBSITE_COLUMNS = (
    'PropId',
    'lblAddress',
    'PropertyClass',
    'Zoning',
    'MapLot',
    'LandArea',
    'TaxDistrict',
    'Owner',
    'Style',
    'Occupancy',
    'NumStories',
    'FloorLocation',
    'LivingArea',
    'NumberOfUnits',
    'TotalRooms',
    'Bedrooms',
    'YearBuilt',
    'OverallCondition',
    'OverallGrade',
    'FirstFloor_GrossArea',
    'PropertyImageLink',
    'gis',
)

WEBSITE_INT_COLUMNS = (
    'PropId',
    'LandArea',
    'NumStories',
    'FloorLocation',
    'LivingArea',
    'NumberOfUnits',
    'TotalRooms',
    'Bedrooms',
    'YearBuilt',
    'FirstFloor_GrossArea',
)

MASTER_LIST_COLUMNS = (
    'OBJECTID',
    'address_id',
    'BldgID',
    'ml',
    'StNm',
    'StName',
    'Full_Addr',
    'TYPE',
    'Entry',
    'lon',
    'lat',
    'Zip_Code',
    'Neighborhood',
    'Ward',
    'Precinct',
    'Block2010',
    'Tract2010',
    'BLKGRP2010',
    'Block2020',
    'Tract2020',
    'BLKGRP2020',
)

MASTER_LIST_INT_COLUMNS = (
    'OBJECTID',
    'Block2010',
    'Tract2010',
    'BLKGRP2010',
    'Block2020',
    'Tract2020',
    'BLKGRP2020',
)

MASTER_LIST_FLOAT_COLUMNS = (
    'lon',
    'lat',
)

GIS_COLUMNS = (
    'PropertyID',
    'PID',
    'Address',
    'LandArea',
    'LandUse',
    'LivingArea',
)

GIS_INT_COLUMNS = (
    'PID',
    'LandArea',
    'LivingArea',
)

class Entry:
    def __init__(self, attrs, required_columns=None, int_columns=None, float_columns=None):
        self.attrs = dict(attrs or {}) ## Copy
        required_columns = required_columns or []
        int_columns      = int_columns      or []
        float_columns    = float_columns    or []

        ## Fix missing
        for key in required_columns:
            if key not in self.attrs:
                self.attrs[key] = None

        ## Fix numbers
        for key in int_columns:
            try:
                if self.attrs[key] is not None:
                    self.attrs[key] = int(self.attrs[key].replace(',', ''))
            except ValueError:
                pass

        for key in float_columns:
            try:
                if self.attrs[key] is not None:
                    self.attrs[key] = float(self.attrs[key].replace(',', ''))
            except ValueError:
                pass

        ## Set attributes
        for attr, val in self.attrs.items():
            if val == '':
                setattr(self, attr, None)
            else:
                setattr(self, attr, val)

    def getPropertyId(self):
        ## pylint: disable=no-self-use
        return None

    def getBuildingId(self):
        ## pylint: disable=no-self-use
        return None

    def getMapLot(self):
        ## pylint: disable=no-self-use
        return None

    def isBuilding(self):
        ## pylint: disable=no-self-use
        return None

    def isProperty(self):
        ## pylint: disable=no-self-use
        return None


class MainDatabaseEntry(Entry):
    def __init__(self, **attrs):
        Entry.__init__(self, attrs, MAIN_COLUMNS, MAIN_INT_COLUMNS, MAIN_FLOAT_COLUMNS)

    def getPropertyId(self):
        if self.PID is None:
            raise MissingDataError('PID')

        return self.PID

    def getMapLot(self):
        return self.MapLot

    def getBuildingId(self):
        return self.GISID

    def isBuilding(self):
        return (self.MapLot is None or self.MapLot == self.GISID)


class WebsiteDatabaseEntry(Entry):
    def __init__(self, **attrs):
        Entry.__init__(self, attrs, WEBSITE_COLUMNS, WEBSITE_INT_COLUMNS)

    def getPropertyId(self):
        return self.PropId

    def getBuildingId(self):
        return '_'.join(self.MapLot.split('-')[:2])

    def getMapLot(self):
        return self.MapLot

    def isBuilding(self):
        return (self.MapLot.count('-') == 1)

    def isProperty(self):
        return (self.MapLot.count('-') == 2)


class MasterListEntry(Entry):
    def __init__(self, **attrs):
        Entry.__init__(self, attrs, MASTER_LIST_COLUMNS, MASTER_LIST_INT_COLUMNS, MASTER_LIST_FLOAT_COLUMNS)

    @property
    def Block(self):
        if self.Block2020 is None:
            return self.Block2010

        return self.Block2020

    @property
    def Tract(self):
        if self.Tract2020 is None:
            return self.Tract2010

        return self.Tract2020

    @property
    def BLKGRP(self):
        if self.BLKGRP2020 is None:
            return self.BLKGRP2010

        return self.BLKGRP2020

    def getPropertyId(self):
        if self.ml is None:
            raise MissingDataError('ml')

        return self.ml

    def getBuildingId(self):
        return self.ml

    def isBuilding(self):
        return True

    def isProperty(self):
        return False

    def toJson(self):
        return {
            'id':            self.ml,
            'object_id':     self.OBJECTID,
            'street_number': self.StNm,
            'street_name':   self.StName,
            'full_address':  self.Full_Addr,
            'type':          self.TYPE,
            'location':      (self.lon, self.lat),
            'zipcode':       self.Zip_Code,
            'neighborhood':  self.Neighborhood,
            'block':         self.Block,
            'block_group':   self.BLKGRP,
            'tract':         self.Tract,
        }


class GisEntry(Entry):
    def __init__(self, **attrs):
        Entry.__init__(self, attrs, GIS_COLUMNS, GIS_INT_COLUMNS)

    def getPropertyId(self):
        return self.PID

    def getMapLot(self):
        return self.PropertyID

    def getBuildingId(self):
        """Return the building ID of the property"""
        ## Only the first two numbers are the building ID
        return '_'.join(self.PropertyID.split('-')[:2])

    def isBuilding(self):
        return (self.PropertyID.count('-') == 1)

    def isProperty(self):
        return (self.PropertyID.count('-') == 2)


class MissingDataError(Exception):
    def __init__(self, name):
        Exception.__init__(self, f"No source for information found for '{name}'")
        self.name = name


class CombinedEntry:
    ## pylint: disable=too-many-public-methods
    def __init__(self, main_entry, *, website_entry=None, gis_entry=None):
        self.main_entry: MainDatabaseEntry       = main_entry
        self.website_entry: WebsiteDatabaseEntry = website_entry
        self.gis_entry: GisEntry                 = gis_entry
        self._selfValidate()

    @property
    def id(self):
        return self.main_entry.getPropertyId()

    @property
    def building_id(self):
        return self.main_entry.getBuildingId()

    @property
    def address(self):
        ## Preferibly use the text from the website
        if self.website_entry is not None:
            return self.website_entry.lblAddress

        ## Construct address from the main entry
        addr = self.main_entry.Address
        if self.main_entry.Unit is not None:
            addr += ' ' + self.main_entry.Unit

        return addr

    @property
    def zone(self):
        return self.main_entry.Zoning

    @property
    def map_lot(self):
        return self.main_entry.MapLot

    @property
    def num_units(self):
        return self.main_entry.Interior_NumUnits

    @property
    def num_stories(self):
        return self.main_entry.Exterior_NumStories

    @property
    def floor_location(self):
        return self.main_entry.Exterior_FloorLocation

    @property
    def land_area(self):
        if self.gis_entry is not None:
            return self.gis_entry.LandArea

        return self.main_entry.LandArea

    @property
    def living_area(self):
        return self.main_entry.Interior_LivingArea

    @property
    def year_built(self):
        return self.main_entry.Condition_YearBuilt

    @property
    def first_floor_area(self):
        if self.website_entry is not None:
            return self.website_entry.FirstFloor_GrossArea

        return None

    @property
    def total_rooms(self):
        return self.main_entry.Interior_TotalRooms

    @property
    def bedrooms(self):
        return self.main_entry.Interior_Bedrooms

    @property
    def property_class(self):
        if self.main_entry.PropertyClass is None:
            raise MissingDataError('PropertyClass')

        return self.main_entry.PropertyClass

    def setWebsiteEntry(self, website_entry:WebsiteDatabaseEntry):
        self.website_entry = website_entry
        self._selfValidate()

    def setGisEntry(self, gis_entry:GisEntry):
        self.gis_entry = gis_entry
        self._selfValidate()

    def isBuilding(self):
        return (self.main_entry.MapLot is None)

    def toJson(self):
        return {
            'id':               self.id,
            'building_id':      self.building_id,
            'address':          self.address,
            'property_class':   self.property_class,
            'zone':             self.zone,
            'map_lot':          self.map_lot,
            'num_units':        self.num_units,
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


class Database:
    def __init__(self, path, data_type, *, delimiter=None, verbose=False):
        self.path = path
        self.entries = []
        self.by_pid = {}
        self.by_map_lot = {}
        self.by_building_id = defaultdict(list)
        if verbose:
            print(f"Loading {path}")

        with open(path, 'r', encoding="utf-8-sig") as f:
            reader = None
            if delimiter is None:
                reader = csv.DictReader(f)
            else:
                reader = csv.DictReader(f, delimiter=delimiter)

            for row in reader:
                try:
                    entry = data_type(**row)
                    self.entries.append(entry)
                    self.by_pid[entry.getPropertyId()] = entry
                    self.by_map_lot[entry.getMapLot()] = entry
                    self.by_building_id[entry.getBuildingId()].append(entry)
                except Exception as e:
                    print(f"Error while processing {data_type} entry:", row)
                    raise(e)

    def __getitem__(self, key):
        return self.by_pid[key]

    def __contains__(self, key):
        return (key in self.by_pid)

    def __iter__(self):
        return iter(self.entries)


class MainDatabase(Database):
    def __init__(self, path, **kwargs):
        Database.__init__(self, path, MainDatabaseEntry, **kwargs)


class WebsiteDatabase(Database):
    def __init__(self, path, **kwargs):
        Database.__init__(self, path, WebsiteDatabaseEntry, delimiter="\t", **kwargs)


class GisDatabase(Database):
    def __init__(self, path, **kwargs):
        Database.__init__(self, path, GisEntry, delimiter="\t", **kwargs)


class MasterDatabase(Database):
    def __init__(self, path, **kwargs):
        Database.__init__(self, path, MasterListEntry, **kwargs)

    def __getitem__(self, key):
        return self.by_building_id[key]

    def __contains__(self, key):
        return (key in self.by_building_id)
