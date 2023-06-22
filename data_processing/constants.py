## Zones
ZONES_RES = ("A-1", "A-2", "B", "C", "C-1", "C-1A")
ZONES_INTS = ("C-3", "C-3A", "C-3B", "C-3", "C-3A", "C-3B")
ZONES_BIZ_LOW = ("BA", "BA-1", "BA-2", "BA-3", "BA-4", "BC", "O-1")
ZONES_BIZ_HIGH = ("BB", "BB-1", "BB-2", "O-2", "O-3", "C-2B")
ZONES_IND = ("IA", "IA-1" "IA-2", "IB", "IB-1", "IB-2", "IC")
ZONES_OTHER =  ("O-2A", "O-3A", "MXD", "ASD")
ALL_ZONES = ZONES_RES + ZONES_INTS + ZONES_BIZ_LOW + ZONES_BIZ_HIGH + ZONES_IND + ZONES_OTHER

FAR_ZONES = {
    "A-1":  0.5,
    "A-2":  0.5,
    "B":    0.5,
    "C":    0.6,
    "C-1":  0.75,
    "BA":   1.75,
    "BA-1": 1.00,
    "BA-2": 1.75,
    "BA-3": 1.75,
    "BA-4": 1.75,
    "BB":   4,
    "BB-1": 3.24,
    "BB-2": 3.0,
    "BC":   2.0,
}

OS_ZONES = {
    "A-1":  50,
    "A-2":  50,
    "B":    40,
    "C":    36,
    "C-1":  30,
    "BA":   None,
    "BA-1": None,
    "BA-2": None,
    "BA-3": 30,
    "BA-4": None,
    "BB":   None,
    "BB-1": 15,
    "BB-2": 15,
    "BC":   None,
}

LADU_ZONES = {
    "A-1":  6000,
    "A-2":  4500,
    "B":    2500,
    "C":    1800,
    "C-1":  1500,
    "BA":   600,
    "BA-1": 1200,
    "BA-2": 600,
    "BA-3": 1500,
    "BA-4": 600,
    "BB":   300,
    "BB-1": 300,
    "BB-2": 300,
    "BC":   500,
}


## Blocks
FIRST_ST  = (483, 526, 547, 566, 571, 505, 468)
COURT     = (502, 479)
KENDAL    = (680,)
MID_MASS  = (524, 539, 493, 490, 501, 506)


## Neighborhoods
NEIGHBORHOODS = (
    'Area 2/MIT', 'Baldwin', 'Cambridge Highlands', 'Cambridgeport',
    'East Cambridge', 'Mid-Cambridge', 'Neighborhood Nine', 'None',
    'North Cambridge', 'Riverside', 'Strawberry Hill', 'The Port',
    'Wellington-Harrington', 'West Cambridge',
)


## Property
PROPERTY_CLASS = (
    '121 Corporation',
    '4-8-UNIT-APT',
    '>8-UNIT-APT',
    'AFFORDABLE APT',
    'ASSISTED-LIV',
    'AUTO-REPAIR',
    'AUTO-SALES',
    'AUTO-SUPPLY',
    'BANK',
    'BOARDING-HSE',
    'CHILD-CARE',
    'CLEAN-MANUF',
    'COM-DEV-LAND',
    'COM-PDV-LAND',
    'COM-UDV-LAND',
    'CONDO-BLDG',
    'CONDOMINIUM',
    'Cemeteries',
    'Charitable Svc',
    'Church',
    'DCR- State Parks and Rec',
    'DORM-RS-HALL',
    'EATING-ESTBL',
    'ELEC GEN PLANT',
    'ELECT-PLANT',
    'FRAT-ORGANIZ',
    'FRAT-SORORTY',
    'GAS-CONTROL',
    'GAS-STATION',
    'GEN-OFFICE',
    'HIGH-TECH',
    'HOTEL',
    'Hospitals',
    'Housing Authority',
    'Housing, Other',
    'IND-DEV-LAND',
    'INN-RESORT',
    'INV-OFFICE',
    'Improved City',
    'Improved Local Edu',
    'Improved Public Safety',
    'Imprvd County Admin',
    'MANUFACTURNG',
    'MEDICAL-OFFC',
    'MULT-RES-1FAM',
    'MULT-RES-2FAM',
    'MULT-RES-3FAM',
    'MULT-RES-4-8-APT',
    'MULT-RES->8 APT',
    'MULTIPLE-RES',
    'MULTIUSE-COM',
    'MULTIUSE-IND',
    'MULTIUSE-RES',
    'MXD 4-8-UNIT-APT',
    'MXD >8-UNIT-APT',
    'MXD GEN-OFFICE',
    'MXD HIGH-TECH',
    'MXD INV-OFFICE',
    'MXD RETAIL-STORE',
    'MXD SNGL-FAM-RES',
    'MXD THREE-FM-RES',
    'MXD TWO-FAM-RES',
    'NURSING-HOME',
    'Other',
    'Other Charitable',
    'Other Educational',
    'Other Open Space',
    'Other- Scientific',
    'PARKING-GAR',
    'PARKING-LOT',
    'PUB UTIL REG',
    'Private College, University',
    'Private Elementary Education',
    'Private Secondary Education',
    'RES LND-IMP PT DEV',
    'RES LND-IMP UNDEV',
    'RES-&-DEV-FC',
    'RES-COV-PKG',
    'RES-DEV-LAND',
    'RES-LAND-IMP',
    'RES-PDV-LAND',
    'RES-UDV-LAND',
    'RES-UDV-PARK LND',
    'RETAIL-OFFIC',
    'RETAIL-STORE',
    'Rectory, Parsonage',
    'SH-CNTR/MALL',
    'SINGLE FAM W/AUXILIARY APT',
    'SNGL-FAM-RES',
    'SUPERMARKET',
    'TELE-EXCH-STA',
    'TENNIS-CLUB',
    'THEATRE',
    'THREE-FM-RES',
    'TWO-FAM-RES',
    'Transportation Authority',
    'US Government',
    'Utility Authority',
    'Vacant (Private Ed)',
    'Vacant City',
    'Vacant Local Education',
    'Vacant Utility Authority',
    'Vacant, Tax Title',
    'Vacnt Transport Authorit',
    'WAREHOUSE'
)

SNG_FAM_PROPERTY_CLASS = (
    'SINGLE FAM W/AUXILIARY APT',
    'SNGL-FAM-RES',
    'MXD SNGL-FAM-RES',
)

TWO_FAM_PROPERTY_CLASS = (
    'MXD TWO-FAM-RES',
    'TWO-FAM-RES',
)

MULTI_FAM_PROPERTY_CLASS = (
    '4-8-UNIT-APT',
    '>8-UNIT-APT',
    'CONDO-BLDG',
    'CONDOMINIUM',
    'FRAT-ORGANIZ',
    'FRAT-SORORTY',
    'MULT-RES-1FAM',
    'MULT-RES-2FAM',
    'MULT-RES-3FAM',
    'MULT-RES-4-8-APT',
    'MULT-RES->8 APT',
    'MULTIPLE-RES',
    'MULTIUSE-RES',
    'MXD 4-8-UNIT-APT',
    'MXD >8-UNIT-APT',
    'MXD THREE-FM-RES',
    'THREE-FM-RES',
)

OTHER_RES_PROPERTY_CLASS = (
    'AFFORDABLE APT',
    'ASSISTED-LIV',
    'Housing, Other',
    'NURSING-HOME',
)
