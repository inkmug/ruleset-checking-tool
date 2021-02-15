from rct229.rule_engine.rule_base import RuleDefinitionBase, RuleDefinitionListIndexedBase
from rct229.rule_engine.utils import _assert_equal_rule, _select_equal_or_lesser
from rct229.rule_engine.user_baseline_proposed_vals import UserBaselineProposedVals
from rct229.data_fns.table_8_4_4_eff import table_8_4_4_eff
from rct229.data.schema_enums import schema_enums

_TransformerType = schema_enums['TransformerType']

# Rule Definitions for Section 15 of 90.1-2019 Appendix G

# def _check_user_transformer_exists(user_rmr, rmr_context):
#     user_transformers = user_rmr[rmr_context]
#     num_user_transformers = len(user_transformers)
#     if num_user_transformers > 0:
#         applicable = True
#     else:
#         applicable = False
#
#     return applicable


#------------------------

class Section15Rule1(RuleDefinitionBase):
    """Rule 1 of ASHRAE 90.1-2019 Appendix G Section 15 (Transformers).
    """

    def __init__(self):
        id = "15-1"
        description = "Number of transformers modeled in User RMR and Baseline RMR are the same"
        rmr_context = 'transformers'
        rmrs_used = UserBaselineProposedVals(True, True, False)
        super(Section15Rule1, self).__init__(id, description, rmr_context, rmrs_used)

    def check_applicability(self, context):
        return len(context.user) > 0

    def rule_check(self, context):
        user_transformers = context.user
        num_user_transformers = len(user_transformers)

        baseline_transformers = context.baseline
        num_baseline_transformers = len(baseline_transformers)

        outcome = _assert_equal_rule(num_user_transformers, num_baseline_transformers)

        return outcome

#------------------------

class Section15Rule2(RuleDefinitionBase):
    """Rule 2 of ASHRAE 90.1-2019 Appendix G Section 15 (Transformers).
    """

    def __init__(self):
        id = "15-2"
        description = "Number of transformers modeled in User RMR and Proposed RMR are the same"
        rmr_context = 'transformers'
        rmrs_used = UserBaselineProposedVals(True, False, True)
        super(Section15Rule2, self).__init__(id, description, rmr_context, rmrs_used)

    def check_applicability(self, context):
        return len(context.user) > 0

    def rule_check(self, context):
        user_transformers = context.user
        num_user_transformers = len(user_transformers)

        proposed_transformers = context.proposed
        num_proposed_transformers = len(proposed_transformers)

        outcome = _assert_equal_rule(num_user_transformers, num_proposed_transformers)

        return outcome

#------------------------

class Section15Rule3(RuleDefinitionListIndexedBase):
    """Rule 3 of ASHRAE 90.1-2019 Appendix G Section 15 (Transformers).
    """

    def __init__(self):
        super(Section15Rule3, self).__init__(
            id = "15-3",
            description = "User RMR transformer name is in the Proposed RMR",
            rmr_context = 'transformers',
            rmrs_used = UserBaselineProposedVals(True, False, True),
            each_rule = _Section15Rule3_Each(),
            index_rmr = 'user'
        )

    def check_applicability(self, context):
        return len(context.user) > 0

class _Section15Rule3_Each(RuleDefinitionBase):
    def __init__(self):
        super(_Section15Rule3_Each, self).__init__(
            rmrs_used = UserBaselineProposedVals(True, False, True),
        )

    # Override get_context() to jump over the MISSING_CONTEXT check
    def get_context(self, rmrs):
        context = self._get_context(rmrs)
        if context.user is None:
            context = None

        return context

    def rule_check(self, context):
        return context.proposed is not None and context.user['name'] == context.proposed['name']


#------------------------


class Section15Rule4(RuleDefinitionListIndexedBase):
    """Rule 4 of ASHRAE 90.1-2019 Appendix G Section 15 (Transformers).
    """

    def __init__(self):
        super(Section15Rule4, self).__init__(
            id = "15-4",
            description = "User RMR transformer name is in the Baseline RMR",
            rmr_context = 'transformers',
            rmrs_used = UserBaselineProposedVals(True, True, False),
            each_rule = _Section15Rule4_Each(),
            index_rmr = 'user'
        )

    def check_applicability(self, context):
        return len(context.user) > 0



class _Section15Rule4_Each(RuleDefinitionBase):
    def __init__(self):
        super(_Section15Rule4_Each, self).__init__(
            rmrs_used = UserBaselineProposedVals(True, True, False),
        )

    def rule_check(self, context):
        return context.user['name'] == context.baseline['name']

#------------------------


class Section15Rule5(RuleDefinitionListIndexedBase):
    """Rule 5 of ASHRAE 90.1-2019 Appendix G Section 15 (Transformers).
    """

    def __init__(self):
        super(Section15Rule5, self).__init__(
            id = "15-5",
            description = "Transformer efficiency reported in Baseline RMR equals Table 8.4.4",
            rmr_context = 'transformers',
            rmrs_used = UserBaselineProposedVals(True, True, False),
            each_rule = _Section15Rule5_Each(),
            index_rmr = 'baseline'
        )

    def check_applicability(self, context):
        applicable = len(context.baseline) > 0
        return applicable



class _Section15Rule5_Each(RuleDefinitionBase):
    def __init__(self):
        super(_Section15Rule5_Each, self).__init__(
            rmrs_used = UserBaselineProposedVals(True, True, False),
        )
    # TODO: This is incomplete. We need more guidance as to the various cases
    def check_applicability(self, context):
        dry_type = _TransformerType.DRY_TYPE.name
        user_type = context.user['type']
        baseline_type = context.baseline['type']
        user_efficiency = context.user['efficiency']
        user_phase = context.user['phase']
        user_capacity = context.user['capacity']

        return False
        # return baseline_type == dry_type and user_efficiency > table_8_4_4_eff(phase = user_phase, kVA = user_capacity)

    # TODO :We need more guidance regarding the possible cases
    def rule_check(self, context):
        raise NotImplementedError

#------------------------

class Section15Rule6(RuleDefinitionListIndexedBase):
    """Rule 6 of ASHRAE 90.1-2019 Appendix G Section 15 (Transformers).
    """

    def __init__(self):
        super(Section15Rule6, self).__init__(
            id = "15-6",
            description = "Transformer efficiency reported in User RMR equals Table 8.4.4",
            rmr_context = 'transformers',
            rmrs_used = UserBaselineProposedVals(True, False, False),
            each_rule = _Section15Rule6_Each()
        )

    def check_applicability(self, context):
        applicable = len(context.user) > 0
        return applicable



class _Section15Rule6_Each(RuleDefinitionBase):
    def __init__(self):
        super(_Section15Rule6_Each, self).__init__(
            rmrs_used = UserBaselineProposedVals(True, True, False),
        )

    # TODO: We need more guidance regarding the possible cases
    def check_applicability(self, context):
        return False

    # Override get_context() to jump over the MISSING_CONTEXT check
    def get_context(self, rmrs):
        context = self._get_context(rmrs)
        if context.user is None:
            context = None

        return context

    # TODO: We need more guidance regarding the possible cases
    def rule_check(self, context):
        raise NotImplementedError

#------------------------
