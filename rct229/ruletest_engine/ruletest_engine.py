import copy
import json

# from jsonpointer import JsonPointer
import os

from rct229.rule_engine.engine import evaluate_rule
from rct229.rule_engine.user_baseline_proposed_vals import UserBaselineProposedVals

# Import Rules
from rct229.rules.section6 import *
from rct229.rules.section12 import *
from rct229.rules.section15 import *
from rct229.ruletest_engine.ruletest_jsons.scripts.json_generation_utilities import (
    merge_nested_dictionary,
)
from rct229.schema.validate import validate_rmr
from rct229.utils.json_utils import slash_prefix_guarantee


# Generates the RMR triplet dictionaries from a test_dictionary's "rmr_transformation" element.
# -test_dict = Dictionary with elements 'rmr_transformations' and 'rmr_transformations/user,baseline,proposed'
def generate_test_rmrs(test_dict):
    """Generates the RMR triplet dictionaries from a test_dictionary's "rmr_transformation" element.

    Parameters
    ----------
    test_dict : dict
        A dictionary including an optional rmr_template field and a
        required rmr_transformations field.

        If rmr_template is included, it is used as the starting point
        for each RMR; if not included, the empty dictionary {} is used.

        The rmr_transformations field has optional user, baseline,
        and proposed fields. If any of these fields is present, its
        corresponding RMR will be built by transforming the rmr_template. If
        the user, baseline, or proposed fields are missing, then its
        correponding RMR is set to None.

        The transformations are made using jsonpointer and its set method.
        For example, if rmr_transformations includes
        {
            "user": {
                "ptr1": value1,
                "ptr2": value2
            }
        }
        then the user RMR will be produced by first treating "ptr1" as a
        JsonPointer into rmr_template and setting the pointed to node to value1,
        which can be of any type; and then repeating the process for "ptr2" and
        value2. Note that the set method of JsonPointer will create any missing
        fields along the path to the pointer, but will NOT add elements to a
        list.

    Returns
    -------
    tuple : a triplet containing:
        - user_rmr (dictionary): User RMR dictionary built from RMR Transformation definition
        - baseline_rmr (dictionary): Baseline RMR dictionary built from RMR Transformation definition
        - proposed_rmr (dictionary): Proposed RMR dictionary built from RMR Transformation definition
    """

    # The rmr_transformations field is required
    if "rmr_transformations" not in test_dict:
        test_dict["rmr_transformations"] = {}

    # Each of these will remain None unless it is specified in
    # rmr_transformations. If its transfomration is set to {}, then it
    # will simply be a copy of rmr_template
    user_rmr = None
    baseline_rmr = None
    proposed_rmr = None

    # If RMRs are based on a template
    if "rmr_template" in test_dict:

        # Get a copy of the RMR template dictionary
        rmr_template = test_dict["rmr_template"]

        # Initialize user/baseline/proposed RMRs with template if the rmr_template dictionary references them
        if "user" in rmr_template:
            user_rmr = copy.deepcopy(rmr_template["json_template"])

            if "user" not in test_dict["rmr_transformations"]:
                test_dict["rmr_transformations"]["user"] = {}

        if "baseline" in rmr_template:
            baseline_rmr = copy.deepcopy(rmr_template["json_template"])

            if "baseline" not in test_dict["rmr_transformations"]:
                test_dict["rmr_transformations"]["baseline"] = {}

        if "proposed" in rmr_template:
            proposed_rmr = copy.deepcopy(rmr_template["json_template"])

            if "proposed" not in test_dict["rmr_transformations"]:
                test_dict["rmr_transformations"]["proposed"] = {}

    # Read in transformations dictionary. This will perturb a template or fully define an RMR (if no template defined)
    rmr_transformations_dict = test_dict["rmr_transformations"]

    # If user/baseline/proposed RMR transformations exist, either update their existing template or set them directly
    # from RMR transformations
    if "user" in rmr_transformations_dict:

        # If RMR dictionary is not initialized by a template, initialize it
        if user_rmr is None:
            user_rmr = {}

        merge_nested_dictionary(user_rmr, rmr_transformations_dict["user"])
        # user_rmr.update(rmr_transformations_dict["user"])

    if "baseline" in rmr_transformations_dict:

        # If RMR dictionary is not initialized by a template, initialize it
        if baseline_rmr is None:
            baseline_rmr = {}

        merge_nested_dictionary(baseline_rmr, rmr_transformations_dict["baseline"])
        # baseline_rmr.update(rmr_transformations_dict["baseline"])

    if "proposed" in rmr_transformations_dict:

        # If RMR dictionary is not initialized by a template, initialize it
        if proposed_rmr is None:
            proposed_rmr = {}

        merge_nested_dictionary(proposed_rmr, rmr_transformations_dict["proposed"])
        # proposed_rmr.update(rmr_transformations_dict["proposed"])

    return user_rmr, baseline_rmr, proposed_rmr


def evaluate_outcome_enumeration_str(outcome_enumeration_str):
    """Returns a boolean for whether a rule passed/failed based on the outcome string enumeration

    Parameters
    ----------
    outcome_enumeration_str : str

        String equal to a set of predetermined enumerations for rule outcomes. These enumerations describe things such
        as whether a test passed, failed, required manual check, etc.

    Returns
    -------
    test_result : bool

        Boolean describing whether the rule should be treated as passing or failing. Pass = True, Fail = False
    """

    # Check result of rule evaluation against known string constants
    # (TODO: these constants should be stored elsewhere rather than called directly)
    if outcome_enumeration_str == "PASSED":
        test_result = True
    elif outcome_enumeration_str == "FAILED":
        test_result = False
    elif outcome_enumeration_str == "MANUAL_CHECK_REQUIRED":
        test_result = False
    elif outcome_enumeration_str == "MISSING_CONTEXT":
        test_result = False
    elif outcome_enumeration_str == "NA":
        test_result = False
    else:
        raise ValueError(
            f"OUTCOME: The enumeration {outcome_enumeration_str} does not have a test result interpretation."
        )

    return test_result


def process_test_result(test_result, test_dict, test_id):
    """Returns a string describing whether or not a test resulted in its expected outcome

    Parameters
    ----------
    test_result : bool

        Boolean for whether or not a test passed. Passed = True, Failed = False

    test_dict : dict

        Python dictionary containing the a test's expected outcome and description

    test_id: str

        String describing the test's section, rule, and test case ID (e.g. rule-15-1a)

    Returns
    -------

    outcome_text: str

        String describing whether or not a test resulted in its expected outcome

    received_expected_outcome: bool

        Boolean describing if the ruletest resulted in the expected outcome (i.e., passed when expected to pass,
        failed when expected to fail)

    """

    # Get reporting parameters. Check if the test is expected to pass/fail and read in the description.
    expected_outcome = test_dict["expected_rule_outcome"] == "pass"
    description = test_dict["description"]

    # Check if the test results agree with the expected outcome. Write an appropriate response based on their agreement
    received_expected_outcome = test_result == expected_outcome

    # Check if the test results agree with the expected outcome. Write an appropriate response based on their agreement
    if received_expected_outcome:

        if test_result:
            # f"SUCCESS: Test {test_id} passed as expected. The following condition was identified: {description}"
            outcome_text = None
        else:
            # f"SUCCESS: Test {test_id} failed as expected. The following condition was identified: {description}"
            outcome_text = None

    else:

        if test_result:
            outcome_text = f"FAILURE: Test {test_id} passed unexpectedly. The following condition was not identified: {description}"
        else:
            outcome_text = f"FAILURE: Test {test_id} failed unexpectedly. The following condition was not identified: {description}"

    return outcome_text, received_expected_outcome


def run_section_tests(test_json_name):
    """Runs all tests found in a given test JSON and prints results to console. Returns true/false describing whether
    or not all tests in the JSON result in the expected outcome.

    Parameters
    ----------
    test_json_name : string

        Name of test JSON in 'test_jsons' directory. (e.g., transformer_tests.json)

    Returns
    -------
    all_tests_successful : bool

        Boolean describing if all tests in the JSON result in the expected outcome.
    """

    # Create path to test JSON (e.g. 'transformer_tests.json')
    test_json_path = os.path.join(
        os.path.dirname(__file__), "ruletest_jsons", test_json_name
    )

    # hash for capturing test results. Keys include: "results, log"
    test_result_dict = {}
    test_result_dict["results"] = []
    test_result_dict["errors"] = []

    # Initialize statistics
    n_errors = 0
    n_missing_rules = 0

    banner = [
        #"",
        #"*****************************************************************",
        #"ASHRAE STD 229P RULESET CHECKING TOOL",
        #"Project Testing Workflow",
        #"Ruleset: ASHRAE 90.1-2019 Performance Rating Method (Appendix G)",
        #"*****************************************************************",
        #"",
        #"----------------------------------",
        #f"TESTING {test_json_name}...",
        #"----------------------------------",
        #"",
        f"  {test_json_name}...",
    ]

    for line in banner:
        print(line)

    # Open
    with open(test_json_path) as f:
        test_list_dictionary = json.load(f)

    # Cycle through tests in test JSON and run each individually
    for test_id in test_list_dictionary:

        # Load next test dictionary from test list
        test_dict = test_list_dictionary[test_id]

        # Generate RMR dictionaries for testing
        user_rmr, baseline_rmr, proposed_rmr = generate_test_rmrs(test_dict)
        rmr_trio = UserBaselineProposedVals(user_rmr, baseline_rmr, proposed_rmr)

        # Identify Section and rule
        section = test_dict["Section"]
        rule = test_dict["Rule"]

        # Construction function name for Section and rule
        function_name = f"Section{section}Rule{rule}"

        test_result_dict["log"] = []  # Initialize log for this test result
        test_result_dict[
            f"{test_id}"
        ] = []  # Initialize log of this tests multiple results
        had_errors = False

        # Pull in rule, if written. If not found, fail the test and log which Section and Rule could not be found.
        try:
            rule = globals()[function_name]()
        except KeyError:

            # Print message communicating that a rule cannot be found
            print(f"RULE NOT FOUND: {function_name}. Cannot test {test_id}")

            # Append failed message to rule
            test_result_dict["results"].append(False)
            n_missing_rules += 1
            continue

        # Evaluate rule and check for invalid RMRs
        evaluation_dict = evaluate_rule(rule, rmr_trio)
        invalid_rmrs_dict = evaluation_dict["invalid_rmrs"]

        # If invalid RMRs exist, fail this rule and append failed message
        if len(invalid_rmrs_dict) != 0:

            # Find which RMRs were invalid
            for invalid_rmr, invalid_rmr_message in invalid_rmrs_dict.items():

                # Print message communicating that the schema is invalid
                print(
                    f"INVALID SCHEMA: Test {test_id}: {invalid_rmr} RMR: {invalid_rmr_message}"
                )

            # Append failed message to rule
            test_result_dict["results"].append(False)
            n_errors += 1

        # If RMRs are valid, check their outcomes
        else:

            # Check the evaluation dictionary "outcomes" element
            # NOTE: The outcome structure can either be a string for a single result or a list of dictionaries with
            # multiple results based on the Rule being tested.
            outcome_structure = evaluation_dict["outcomes"][0]

            # Update test_results_dict "log" and f"{test_id}" keys.
            # -The "log" element contains a list string describing errors, if any.
            # -The f"{test_id} element contains a list of booleans describing whether or not each testable element in
            #  outcome structure met the expected outcome for this test_id
            evaluate_outcome_object(
                outcome_structure, test_result_dict, test_dict, test_id
            )

            # Check set of results for this test ID against expected outcome
            if test_dict["expected_rule_outcome"] == "pass":

                # For an expected pass, ALL tested elements in the RMR triplet must pass
                if not all(test_result_dict[f"{test_id}"]):

                    had_errors = True

            elif test_dict["expected_rule_outcome"] == "fail":

                # If all elements don't meet the expected outcome, flag this as an error
                if not any(test_result_dict[f"{test_id}"]):
                    had_errors = True

            # If errors were found, communicate the error logs
            if had_errors:

                n_errors += 1

                # Catalogue errors
                for test_result_string in test_result_dict["log"]:

                    # TODO: instead of reinitializing "log" every test run, append errors to test_result_dict as you go
                    test_result_dict["errors"].append(test_result_string)

                    # print(test_result_string)

    # Process results
    n_tests, n_evaluations = get_number_of_tests_and_evaluations(test_result_dict)
    n_passing = n_tests - n_errors - n_missing_rules

    # Print results to console
    """
    #print("")
    print("RULE TEST EVALUATIONS COMPLETE.")
    #print("----------------------------------")
    print("")
    print("----------------------------------")
    print("TEST SUMMARY")
    print("----------------------------------")
    print("")
    print(f"Number of Tests: {n_tests}")
    #print("Totals")
    #print(f"    Tests: {n_tests}")
    #print(f"    Evaluations: {n_evaluations}")
    #print("")
    print("Test Outcomes")
    print(f"    Passed:{n_tests - n_errors - n_missing_rules}")
    print(f"    Failed:{n_errors}")
    print(f"    Missing Rules:{n_missing_rules}")
    print("")  # Buffer line
    print("----------------------------------")
    """

    if n_errors != 0:

        print("")
        print("ERRORS:")
        print("----------------------------------")
        # Print errors
        for error_string in test_result_dict["errors"]:
            print(error_string)

    # Return whether or not all tests in this test JSON received their expected outcome as a boolean
    all_tests_successful = all(test_result_dict["results"])

    #return all_tests_successful
    return {
            "all_tests_succesful": all_tests_successful,
            "number_tests": n_tests,
            "number_passing_tests": n_passing, 
            "number_failing_tests": n_errors, 
            "number_missing_rules": n_missing_rules
        }


def validate_test_json_schema(test_json_path):
    """Evaluates a test JSON against the JSON schema. Raises flags for any errors found in any rule tests. Results
    are printed to console

    Parameters
    ----------
    test_json_path : string

        Path to the test JSON in 'test_jsons' directory. (e.g., transformer_tests.json)

    """

    # List capturing messages describing failed RMR schemas
    failure_list = []

    # Open
    with open(test_json_path) as f:
        test_list_dictionary = json.load(f)

    # Cycle through tests in test JSON and run each individually
    for test_id in test_list_dictionary:
        # Load next test dictionary from test list
        test_dict = test_list_dictionary[test_id]

        # Generate RMR dictionaries for testing
        user_rmr, baseline_rmr, proposed_rmr = generate_test_rmrs(test_dict)

        # Evaluate RMRs against the schema
        user_result = validate_rmr(user_rmr) if user_rmr != None else None
        baseline_result = validate_rmr(baseline_rmr) if baseline_rmr != None else None
        proposed_result = validate_rmr(proposed_rmr) if proposed_rmr != None else None

        results_list = [user_result, baseline_result, proposed_result]
        rmr_type_list = ["User", "Baseline", "Proposed"]

        for result, rmr_type in zip(results_list, rmr_type_list):

            # If result contains a dictionary with failure information, append failure to failure list
            if isinstance(result, dict):

                if result["passed"] is not True:

                    error_message = result["error"]
                    failure_message = f"Schema validation in {test_id} for the {rmr_type} RMR: {error_message}"
                    failure_list.append(failure_message)

    if len(failure_list) == 0:

        base_name = os.path.basename(test_json_path)
        print(f"No schema errors found in {base_name}")
        return True

    else:
        for failure in failure_list:

            print(failure)

        return False


def evaluate_outcome_object(outcome_dict, test_result_dict, test_dict, test_id):
    """Evaluates the outcome of an evaluate_rule function call (can be either a dictionary or a list), comparing it
    against the expected outcome for  given rule test. Results populate the "log" and "test_id" keys in the
    test_result_dict dictionary.

    Parameters
    ----------
    outcome_dict : list or dict

       The evaluate_rule function returns a dictionary with an "outcome" key. This is an instance of the object
       contained in that dictionary.

    test_result_dict: dict

        Dictionary used to log errors and aggregate the test results for a given outcome_dict. Updating this dictionary
        is the chief purpose of this function. Most notably the test_result_dict[f"{test_id}"] element is populated with
        a list of booleans describing whether or not the elements of the outcome_dict meet the expected outcome described
        in test_dict.

    test_dict: dict

       Dictionary containing the rule test RMR triplets, expected outcome, and description information for the ruletest
       being tested against

    test_id: str
       String describing the particular section, rule, and test case for a given rule test (e.g., rule-6-1-a)


    """

    # If the result key is a list of results (i.e. many elements get tested), keep drilling down until you get single
    # dictionary
    if isinstance(outcome_dict["result"], list):

        # Iterate through each outcome in outcome results recursively until you get down to individual results
        for nested_outcome in outcome_dict["result"]:

            # Check outcome of each in list recursively until "result" key is not a list, but a dictionary
            evaluate_outcome_object(
                nested_outcome, test_result_dict, test_dict, test_id
            )  # , outcome_result_list)

    else:

        # Process this tests results
        outcome_enumeration_str = outcome_dict[
            "result"
        ]  # enumeration for result (e.g., PASS, FAIL, CONTEXT_MISSING)

        # Evaluate whether Rule passes or fails, a boolean
        rule_passed = evaluate_outcome_enumeration_str(outcome_enumeration_str)

        # Write outcome text based and "receive_expected_outcome" boolean based on the test result
        outcome_text, received_expected_outcome = process_test_result(
            rule_passed, test_dict, test_id
        )

        # Append results if expected outcome not received
        if not received_expected_outcome:

            # Describe failure if not yet included in log
            if outcome_text not in test_result_dict["log"]:
                test_result_dict["log"].append(outcome_text)

            # Context for the result (e.g., "Space 1"), if included
            outcome_result_context = (
                outcome_dict["name"] if "name" in outcome_dict else "Unknown context"
            )

            # Dictionary of calculated values converted to string
            outcome_calc_vals_string = (
                str(outcome_dict["calc_vals"]) if "calc_vals" in outcome_dict else "N/A"
            )

            test_result_dict["log"].append(
                f"{outcome_result_context}: Calculated values - {outcome_calc_vals_string}"
            )

        test_result_dict[f"{test_id}"].append(received_expected_outcome)


def get_number_of_tests_and_evaluations(test_result_dic):

    """
    Determines the number of tests and evaluations performed after running a test JSON.

    Parameters
    ----------

    test_result_dict: dict

        Dictionary used to log errors and aggregate the test results for a test JSON. This should be fully populated
        once the code reaches this point

    Returns
    -------
    n_tests: int
        The number of tests evaluated
    n_evaluations: int
        The total number of evaluations ran. Many tests run more than one evaluation at a time. This tracks the total.

    """

    n_tests = 0
    n_evaluations = 0

    for key in test_result_dic:

        # Skip any test element that's not a rule (e.g., log)
        if "rule" not in key:
            continue

        # Add number of evaluations for this rule to total
        n_tests += 1
        n_evaluations += len(test_result_dic[key])

    return n_tests, n_evaluations


def run_transformer_tests():
    """Runs all tests found in the transformer tests JSON.

    Returns
    -------
    None

    Results of transformer test are spit out to console
    """

    transformer_rule_json = "transformer_tests.json"

    return run_section_tests(transformer_rule_json)


def run_lighting_tests():
    """Runs all tests found in the lighting tests JSON.

    Returns
    -------
    None

    Results of lighting test are spit out to console
    """

    lighting_test_json = "lighting_tests.json"

    return run_section_tests(lighting_test_json)


def run_receptacle_tests():
    """Runs all tests found in the lighting tests JSON.

    Returns
    -------
    None

    Results of lighting test are spit out to console
    """

    receptacle_json = "receptacle_tests.json"

    return run_section_tests(receptacle_json)
