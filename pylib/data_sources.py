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
    'Exterior_Occupancy',
    'Exterior_NumStories',
    'Exterior_FloorLocation',
    'Interior_LivingArea',
    'Interior_NumUnits',
    'Interior_TotalRooms',
    'Interior_Bedrooms',
    'Condition_YearBuilt',
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
    'NumStories'
    'FloorLocation'
    'LivingArea'
    'NumberOfUnits'
    'TotalRooms',
    'Bedrooms',
    'YearBuilt',
    'FirstFloor_GrossArea',
)

MASTER_LIST_COLUMNS = (
    'OBJECTID',
    'address_id',
    'BldgID',
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

MASTER_LIST_WEBSITE_INT_COLUMNS = (
    'OBJECTID',
    'Ward',
    'Precinct',
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
            self.attrs[key] = int(self.attrs[key].replace(','))

        for key in float_columns:
            self.attrs[key] = float(self.attrs[key].replace(','))

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

    def isBuilding(self):
        ## pylint: disable=no-self-use
        return None

    def isProperty(self):
        ## pylint: disable=no-self-use
        return None


class MainDatabaseEntry(Entry):
    def __init__(self, **attrs):
        Entry.__init__(self, attrs, MAIN_COLUMNS, MAIN_INT_COLUMNS)

    def getPropertyId(self):
        return self.PID

    def getBuildingId(self):
        return self.BldgNum

    def isBuilding(self):
        return (self.MapLot is None)

    def isProperty(self):
        return (self.MapLot is not None)


class WebsiteDatabaseEntry(Entry):
    def __init__(self, **attrs):
        Entry.__init__(self, attrs, WEBSITE_COLUMNS, WEBSITE_INT_COLUMNS)

    def getPropertyId(self):
        return self.PropId

    def getBuildingId(self):
        return '_'.join(self.MapLot.split('-')[:2])

    def isBuilding(self):
        return (self.MapLot.count('-') == 1)

    def isProperty(self):
        return (self.MapLot.count('-') == 2)


class MasterListEntry(Entry):
    def __init__(self, **attrs):
        Entry.__init__(self, attrs, MASTER_LIST_COLUMNS, MASTER_LIST_WEBSITE_INT_COLUMNS, MASTER_LIST_FLOAT_COLUMNS)

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

    def getBuildingId(self):
        return self.BldgID

    def isBuilding(self):
        return True

    def isProperty(self):
        return False


class GisEntry(Entry):
    def __init__(self, **attrs):
        Entry.__init__(self, attrs, GIS_COLUMNS, GIS_INT_COLUMNS)

    def getPropertyId(self):
        return self.PID

    def getBuildingId(self):
        """Return the building ID of the property"""
        ## Only the first two numbers are the building ID
        return '_'.join(self.PropertyID.split('-')[:2])

    def isBuilding(self):
        return (self.PropertyID.count('-') == 1)

    def isProperty(self):
        return (self.PropertyID.count('-') == 2)
