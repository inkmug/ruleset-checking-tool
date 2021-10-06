import rct229

from rct229.data import data
from rct229.data_fns.table_utils import find_osstd_table_entry
from rct229.schema.config import ureg

# This dictionary maps the ExteriorLightingAreas2019ASHRAE901TableG36 enumerations to
# the corresponding lpd_space_type values in the file
# ashrae_90_1_table_3_6.json

building_exterior_enumeration_to_lpd_space_type_map = {
 "UNCOVERED_PARKING_LOTS_AND_DRIVES": "Uncovered parking lots and drives",
 "WALKWAY_NARROW": "Walkway - narrow",
 "WALKWAY_WIDE": "Walkway - wide",
 "PLAZA_AREAS": "Plaza Areas",
 "SPECIAL_FEATURE_AREAS": "Special Feature Areas",
 "STAIRWAYS": "Stairways",
 "MAIN_ENTRANCE_DOOR": "Main entrance door",
 "OTHER_ENTRANCE_OR_EXIT_DOORS": "Other entrance or exit doors",
 "EXTERIOR_CANOPIES": "Exterior canopies",
 "OUTDOOR_SALES_OPEN_AREAS": "Outdoor sales - open areas",
 "STREET_FRONTAGE": "Street frontage",
 "NON_TRADABLE_FACADE": "Non-tradable facade"
}

def table_G3_6_lookup(building_exterior_type_enum_val):
    """Returns the lighting power density for a building_exterior as
    required by ASHRAE 90.1 Table G3.6
    Parameters
    ----------
    building_exterior_type : str
        One of the ExteriorLightingAreas2019ASHRAE901TableG36 enumeration values

    Returns
    -------
    dict
        { lpd: Quantity - The lighting power density in watt per square foot given by Table G3.6, linear_lpd: Quantity - The lighting power density in watt per linear foot given by Table G3.6 }

    """
    building_exterior_type = building_exterior_enumeration_to_lpd_space_type_map[
        building_exterior_type_enum_val
    ]

    osstd_entry = find_osstd_table_entry(
        [("building_exterior_type", building_exterior_type)],
        osstd_table=data["ashrae_90_1_table_3_6"],
    )
    watts_per_ft2 = osstd_entry["w/ft^2"]
    watts_per_linear_ft = osstd_entry["w/ft"]
    if watts_per_linear_ft is None:
        lpd = watts_per_ft2 * ureg("watt / foot**2")
        linear_lpd = None
    elif watts_per_ft2 is None:
       linear_lpd = watts_per_linear_ft * ureg("watt / foot")
       lpd = None
    else:
        lpd = watts_per_ft2 * ureg("watt / foot**2")
        linear_lpd = watts_per_linear_ft * ureg("watt / foot")
    
    return {"lpd": lpd, "linear_lpd": linear_lpd}


