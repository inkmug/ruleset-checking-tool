import rct229
from rct229.data import data
from rct229.data.schema_enums import schema_enums

_osstd_prm_interior_lighting_data = data["ashrae_90_1_prm_2019.prm_interior_lighting"][
    "prm_interior_lighting"
]

# This dictionary maps the LightingSpaceType2019ASHRAE901T951TG38 enumerations to
# the corresponding lpd_space_type values in the OSSTD file
# ashrae_90_1_prm_2019.prm_interior_lighting.json
lighting_space_enumeration_to_lpd_space_type_map = {
    "AUTOMOTIVE_FACILITY": "automotive facility - whole building",
    "CONVENTION_CENTER": "convention center - whole building",
    "COURTHOUSE": "courthouse - whole building",
    "DINING_BAR_LOUNGE_LEISURE": "dining: bar lounge/leisure - whole building",
    "DINING_CAFETERIA_FAST_FOOD": "dining: cafeteria/fast food - whole building",
    "DINING_FAMILY": "dining: family - whole building",
    "DORMITORY": "dormitory - living quarters",
    "EXERCISE_CENTER": "exercise center - whole building",
    "FIRE_STATION": "fire station - whole building",
    "GYMNASIUM": "gymnasium - whole building",
    "HEALTH_CARE_CLINIC": "health-care clinic - whole building",
    "HOSPITAL": "hospital - whole building",
    "HOTEL_MOTEL": "hotel/motel - whole building",
    "LIBRARY": "library - whole building",
    "MANUFACTURING_FACILITY": "manufacturing facility - whole building",
    "MOTION_PICTURE_THEATER": "motion picture theater - whole building",
    "MULTIFAMILY": "multifamily - whole building",
    "MUSEUM": "museum - whole building",
    "OFFICE": "office - whole building",
    "PARKING_GARAGE": "parking garage - whole building",
    "PENITENTIARY": "penitentiary - whole building",
    "PERFORMING_ARTS_THEATER": "performing arts theater - whole building",
    "POLICE_STATION": "police station - whole building",
    "POST_OFFICE": "post office - whole building",
    "RELIGIOUS_FACILITY": "religious facility - whole building",
    "RETAIL": "retail - whole building",
    "SCHOOL_UNIVERSITY": "school/university - whole building",
    "SPORTS_ARENA": "sports arena - whole building",
    "TOWN_HALL": "town hall - whole building",
    "TRANSPORTATION": "transportation - whole building",
    "WAREHOUSE": "warehouse - whole building",
    "WORKSHOP": "workshop - whole building",
}


def _get_osstd_entry(lpd_space_type):
    """Returns an entry for a matching lpd space type from interior lighting data
    Parameters
    ----------
    lpd_space_type : str
        One of the LightingSpaceType2019ASHRAE901TG38 enumeration values
    Returns
    -------
    dict
        The prm interior lighting entry for a given lpd space type

    """
    entries = [
        entry
        for entry in _osstd_prm_interior_lighting_data
        if entry["lpd_space_type"] == lpd_space_type
    ]
    assert len(entries) == 1
    return entries[0]


def table_G3_8_lpd(building_area_type):
    """Returns the lighting power density for a space as
    required by ASHRAE 90.1 Table G3.8
    Parameters
    ----------
    building_area_type : str
        One of the LightingSpaceType2019ASHRAE901TG38 enumeration values
    Returns
    -------
    float
        The lighting power density given by Table G3.8 [W/ft^2]
    """
    lpd_space_type = lighting_space_enumeration_to_lpd_space_type_map[
        building_area_type
    ]
    osstd_entry = _get_osstd_entry(lpd_space_type)
    watts_per_sqft = osstd_entry["w/ft^2"]
    lpd = watts_per_sqft

    return lpd
