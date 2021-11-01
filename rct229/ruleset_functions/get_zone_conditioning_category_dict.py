from rct229.data_fns.table_3_2_fns import table_3_2_lookup
from rct229.schema.config import ureg
from rct229.utils.jsonpath_utils import find_all
from rct229.utils.pint_utils import pint_sum

CAPACITY_THRESHOLD = 3.4 * ureg("Btu/(hr * ft2)")
CRAWLSPACE_HEIGHT_THRESHOLD = 7 * ureg("ft")
ZERO_UA = 0 * ureg("ft2 * Btu / (hr * ft2 * delta_degF)")


def get_zone_conditioning_category_dict(climate_zone, building):
    """Determines the zone conditioning category for every zone in a building

    Parameters
    ----------
    climate_zone : str
        One of the ClimateZone2019ASHRAE901 enumerated values
    building : dict
        A dictionary representing a building as defined by the ASHRAE229 schema
    Returns
    -------
    dict
        A dictionary that maps zones to one of the conditioning categories:
        "CONDITIONED MIXED", "CONDITIONED NON-RESIDENTIAL", "CONDITIONED RESIDENTIAL",
        "SEMI-HEATED", "UNCONDITIONED", "UNENCLOSED"
    """
    system_min_heating_output = table_3_2_lookup(climate_zone)[
        "system_min_heating_output"
    ]

    zone_conditioning_category_dict = {}

    building_zones = find_all("building_segments[*].zones[*]", building)

    building_hvac_systems = find_all(
        "building_segments[*].heating_ventilation_air_conditioning_systems[*]",
        building,
    )
    # Create a map from an hvac system's id to the hvac system itself
    building_hvac_systems_map = dict(
        [(hvac_system["id"], hvac_system) for hvac_system in building_hvac_systems]
    )

    # Determine eligibility for directly conditioned (heated or cooled) and
    # semi-heated zones
    directly_conditioned_zone_ids = []
    semiheated_zone_ids = []
    for zone in building_zones:
        zone_id = zone["id"]

        zone_hvac_systems = [
            building_hvac_systems_map[hvac_system_id]
            for hvac_system_id in zone[
                "served_by_heating_ventilation_air_conditioning_systems"
            ]
        ]
        # Get the first sensible_cool_capacity and heat_capacity from each hvac system
        zone_sensible_cool_capacities = [
            hvac_system["sensible_cool_capacity"][0]
            for hvac_system in zone_hvac_systems
        ]
        zone_heat_capacities = [
            hvac_system["heat_capacity"][0] for hvac_system in zone_hvac_systems
        ]
        # Sum the capcities
        total_zone_sensible_cool_capacity = pint_sum(zone_sensible_cool_capacities)
        total_zone_heat_capacity = pint_sum(zone_heat_capacities)

        if (
            total_zone_sensible_cool_capacity >= CAPACITY_THRESHOLD
            or total_zone_heat_capacity >= system_min_heating_output
        ):
            directly_conditioned_zone_ids.append(zone_id)
        elif total_zone_heat_capacity >= CAPACITY_THRESHOLD:
            semiheated_zone_ids.append(zone_id)

    # Determine eligibility for indirectly conditioned zones
    indirectly_conditioned_zone_ids = []
    for zone in building_zones:
        zone_id = zone["id"]

        if zone_id not in directly_conditioned_zone_ids:
            zone_lighting_space_types = find_all("spaces[*].lighting_space_type", zone)
            any_zone_lighting_space_type_is_atrium = any(
                [
                    lighting_space_type in ["ATRIUM_LOW_MEDIUM", "ATRIUM_HIGH"]
                    for lighting_space_type in zone_lighting_space_types
                ]
            )
            if any_zone_lighting_space_type_is_atrium:
                indirectly_conditioned_zone_ids.append(zone_id)
            else:
                zone_directly_conditioned_ua = ZERO_UA
                zone_other_ua = ZERO_UA
                for surface in zone["surfaces"]:
                    # Calculate the UA for the surface
                    surface_fenestration_ua = sum(
                        [
                            (fenestration["glazing_area"] + fenestration["opaque_area"])
                            * fenestration["u_factor"]
                            for fenestration in surface["fenestration_subsurfaces"]
                        ]
                    )
                    surface_fenestration_area = sum(
                        [(fenestration["glazing_area"] + fenestration["opaque_area"])]
                    )
                    surface_construction_ua = (
                        surface["area"] - surface_fenestration_area
                    ) * surface["construction"]["u_factor"]
                    surface_ua = surface_fenestration_ua + surface_construction_ua

                    # Add the surface UA to one of the running totals for the zone
                    # according to whether the surface is adjacent to a directly conditioned
                    # zone or not
                    adjacent_zone_id = surface["adjacent_zone"]
                    if (
                        surface["adjacent_to"] == "INTERIOR"
                        and adjacent_zone_id in directly_conditioned_zone_ids
                    ):
                        zone_directly_conditioned_ua += surface_ua
                    else:
                        zone_other_ua += surface_ua

                # The zone is indirectly conditioned if it is thermally more strongly
                # connected to directly conditioned zones than to the exterior and other
                # types of zones
                if directly_conditioned_ua > other_ua:
                    indirectly_conditioned_zone_ids.append(zone_id)
    # Taking stock:
    # To this point, we have determined which zones are directly conditioned,
    # semi-heated, or indirectly conditioned.
    # Next we determine whether the zone is residential, non-residential, or mixed.
    for building_segment in building["building_segments"]:
        # Set building_segment_is_residential and building_segment_is_nonresidential flags
        building_segment_is_residential = False
        building_segment_is_nonresidential = False
        building_segment_lighting_building_area_type = building_segment.get(
            "lighting_building_area_type"
        )
        if building_segment_lighting_building_area_type in [
            "DORMITORY",
            "HOTEL_MOTEL",
            "MULTIFAMILY",
        ]:
            building_segment_is_residential = True
        elif building_segment_lighting_building_area_type is not None:
            building_segment_is_nonresidential = True

        for zone in building_segment["zones"]:
            zone_id = zone["id"]
            if (
                zone_id in directly_conditioned_zone_ids
                or zone_id in indirectly_conditioned_zone_ids
            ):
                # Determine zone_has_residential_spaces and zone_has_nonresidential_spaces flags
                zone_has_residential_spaces = False
                zone_has_nonresidential_spaces = False
                for space in zone["spaces"]:
                    space_lighting_space_type = space.get("lighting_space_type")
                    if space_lighting_space_type in [
                        "DORMITORY_LIVING_QUARTERS",
                        "FIRE_STATION_SLEEPING_QUARTERS",
                        "GUEST_ROOM",
                        "DWELLING_UNIT",
                        "HEALTHCARE_FACILITY_NURSERY",
                        "HEALTHCARE_FACILITY_PATIENT_ROOM",
                    ]:
                        zone_has_residential_spaces = True
                    elif space_lighting_space_type is not None:
                        zone_has_nonresidential_spaces = True
                    elif building_segment_is_residential:
                        zone_has_residential_spaces = True
                    elif building_segment_is_nonresidential:
                        zone_has_nonresidential_spaces = True
                    else:
                        zone_has_nonresidential_spaces = True

                if zone_has_residential_spaces and zone_has_nonresidential_spaces:
                    zone_conditioning_category_dict[zone_id] = "CONDITIONED MIXED"
                elif zone_has_residential_spaces:
                    zone_conditioning_category_dict[zone_id] = "CONDITIONED RESIDENTIAL"
                elif zone_has_nonresidential_spaces:
                    zone_conditioning_category_dict[
                        zone_id
                    ] = "CONDITIONED NON-RESIDENTIAL"

            # To get here, the zone is neither directly or indirectly conditioned
            # Check for semi-heated
            elif zone_id in semiheated_zone_ids:
                zone_conditioning_category_dict[zone_id] = "SEMI-HEATED"
            # Check for interior parking spaces
            elif any(
                [
                    lighting_space_type == "PARKING_AREA_INTERIOR"
                    for lighting_space_type in find_all(
                        "spaces[*].lighting_space_type", zone
                    )
                ]
            ):
                zone_conditioning_category_dict[zone_id] = "UNENCLOSED"
            # Check for crawlspace
            elif zone["volume"] / pint_sum(
                find_all("spaces[*].floor_area", zone)
            ) < CRAWLSPACE_HEIGHT_THRESHOLD and any(
                [
                    get_opaque_surface_type(surface) == "FLOOR"
                    and surface["adjacent_to"] == "GROUND"
                    for surface in zone["surfaces"]
                ]
            ):
                zone_conditioning_category_dict[zone_id] = "UNENCLOSED"
            # Check for attic
            elif any(
                [
                    get_opaque_surface_type(surface) == "CEILING"
                    and surface["adjacent_to"] == "EXTERIOR"
                    for surface in zone["surfaces"]
                ]
            ):
                zone_conditioning_category_dict[zone_id] = "UNENCLOSED"
            # Anything else
            else:
                zone_conditioning_category_dict[zone_id] = "UNCONDITIONED"

        return zone_conditioning_category_dict
