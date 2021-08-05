from numpy import sum

from rct229.data.schema_enums import schema_enums
from rct229.rule_engine.rule_base import (
    RuleDefinitionBase,
    RuleDefinitionListIndexedBase,
)
from rct229.rule_engine.user_baseline_proposed_vals import UserBaselineProposedVals
from rct229.utils.jsonpath_utils import find_all

# Rule Definitions for Section 6 of 90.1-2019 Appendix G


# ------------------------


class Section6Rule1(RuleDefinitionListIndexedBase):
    """Rule 1 of ASHRAE 90.1-2019 Appendix G Section 6 (Lighting)"""

    def __init__(self):
        super(Section6Rule1, self).__init__(
            rmrs_used=UserBaselineProposedVals(True, False, True),
            each_rule=Section6Rule1.BuildingRule(),
            index_rmr="proposed",
            id="6-1",
            description="For the proposed building, each space has the same lighting power as the corresponding space in the U-RMR",
            rmr_context="buildings",
        )

    class BuildingRule(RuleDefinitionListIndexedBase):
        def __init__(self):
            super(Section6Rule1.BuildingRule, self).__init__(
                rmrs_used=UserBaselineProposedVals(True, False, True),
                each_rule=Section6Rule1.BuildingRule.SpaceRule(),
                index_rmr="proposed",
                list_path="$..spaces[*]",  # All spaces inside the building
            )

        class SpaceRule(RuleDefinitionBase):
            def __init__(self):
                super(Section6Rule1.BuildingRule.SpaceRule, self,).__init__(
                    required_fields={
                        "$": ["interior_lighting", "floor_area"],
                        "interior_lighting[*]": ["power_per_area"],
                    },
                    rmrs_used=UserBaselineProposedVals(True, False, True),
                )

            def get_calc_vals(self, context, data=None):
                space_lighting_power_per_area_user = sum(
                    find_all("interior_lighting[*].power_per_area", context.user)
                )
                space_lighting_power_per_area_proposed = sum(
                    find_all("interior_lighting[*].power_per_area", context.proposed)
                )

                return {
                    "space_lighting_power_user": space_lighting_power_per_area_user
                    * context.user["floor_area"],
                    "space_lighting_power_proposed": space_lighting_power_per_area_proposed
                    * context.proposed["floor_area"],
                }

            def rule_check(self, context, calc_vals, data=None):
                return (
                    calc_vals["space_lighting_power_user"]
                    == calc_vals["space_lighting_power_proposed"]
                )

class Section6Rule8(RuleDefinitionListIndexedBase):
    """Rule 8 of ASHRAE 90.1-2019 Appendix G Section 6 (Lighting)"""

    def __init__(self):
        super(Section6Rule1, self).__init__(
            rmrs_used=UserBaselineProposedVals(False, True, False),
            each_rule=Section6Rule1.BuildingRule(),
            index_rmr="baseline",
            id="6-8",
            description="The baseline LPD is equal to expected value in Table G3.7 when lighting has been designed and submitted.",
            rmr_context="buildings",
        )

    class BuildingRule(RuleDefinitionListIndexedBase):
        """Rule Definition section applied to each Building.
        """
        def __init__(self):
            super(Section6Rule8.BuildingRule, self).__init__(
                rmrs_used=UserBaselineProposedVals(False, True, False),
                each_rule=Section6Rule1.BuildingRule.SpaceRule(),
                index_rmr="baseline",
                list_path="$..spaces[*]",  # All spaces inside the building
            )

        def is_applicable(self, context, data=None):
            # Function to check if space by space method is used
            is_space_by_space_method_used = check_lighting_space_by_space_method(context.baseline)
            
            #Return TRUE if space by space method is used.  Otherwise, return FALSE.
            return is_space_by_space_method_used

        class SpaceRule(RuleDefinitionBase):
            """Rule Definition section to be applied to each Space in a Building.
            """
            def __init__(self):
                super(Section6Rule8.BuildingRule.SpaceRule, self,).__init__(
                    # Data elements to be extracted from RMR
                    required_fields={
                        "interior_lighting[*]": ["power_per_area"],
                    },
                    rmrs_used=UserBaselineProposedVals(True, False, True),
                )

            def get_calc_vals(self, context, data=None):
                """Function to return calculated values from Space data groups.
                """                
                space_lighting_power_per_area = sum(
                    find_all("interior_lighting[*].power_per_area", context.baseline)
                )
                lighting_space_type = context.user["lighting_space_type"]
                interior_lighting_power_allowance = table_G3_7(space_type=lighting_space_type)

                return {
                    "space_lighting_power_per_area": space_lighting_power_per_area,
                    "interior_lighting_power_allowance": interior_lighting_power_allowance,
                }

            def rule_check(self, context, calc_vals, data=None):
                """Function defining the logical assertion of Rule 6-8.
                    i.e. Baseline LPD for a space is equal to Table G3.7 lighting power allowance.
                    Return TRUE if assertion is valid.  Returns FALSE is assertion is invalid.
                """
                return (
                    calc_vals["space_lighting_power_per_area"]
                    == calc_vals["interior_lighting_power_allowance"]
                )
# ------------------------
