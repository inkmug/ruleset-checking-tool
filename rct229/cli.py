import click

from rct229.reports.project_report import (
    #print_json_report,
    write_json_report,
    write_rule_evaluation_report,
    #print_rule_report,
    print_summary_report
)
from rct229.reports.software_testing_report import print_summary_report as print_software_summary_report

from rct229.rule_engine.engine import evaluate_all_rules
from rct229.ruletest_engine.ruletest_engine import run_section_tests
from rct229.schema.validate import validate_rmr
from rct229.utils.file import deserialize_rmr_file

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def print_version():
    click.echo(f"{__name__}, version {__version__}")


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(None, "-v", "--version")
def cli():
    """
    ASHRAE 229 - Ruleset Checking Tool
    """


# Evaluate RMR Triplet
short_help_text = "Run Project Testing Workflow on RMR triplet."
help_text = short_help_text
@cli.command("run_project_tests", short_help=short_help_text, help=help_text, hidden=True)
@click.argument("user_rmr", type=click.File("rb"))
@click.argument("baseline_rmr", type=click.File("rb"))
@click.argument("proposed_rmr", type=click.File("rb"))
def run_project_tests(user_rmr, baseline_rmr, proposed_rmr):
    print("")
    print("*****************************************************************")
    print("ASHRAE STD 229P RULESET CHECKING TOOL")
    print("Project Testing Workflow")
    print("Ruleset: ASHRAE 90.1-2019 Performance Rating Method (Appendix G)")
    print("*****************************************************************")
    print("")
    print("----------------------------------")
    print("READING RMR FILES...")
    print(f"  User: {user_rmr.name}")
    print(f"  Baseline: {baseline_rmr.name}")
    print(f"  Proposed: {proposed_rmr.name}")
    print("----------------------------------")
    print("")

    user_rmr_obj = None
    baseline_rmr_obj = None
    proposed_rmr_obj = None
    rmr_are_valid_json = True
    try:
        user_rmr_obj = deserialize_rmr_file(user_rmr)
    except:
        rmr_are_valid_json = False
        print("User RMR is not a valid JSON file")
    try:
        baseline_rmr_obj = deserialize_rmr_file(baseline_rmr)
    except:
        rmr_are_valid_json = False
        print("Baseline RMR is not a valid JSON file")
    try:
        proposed_rmr_obj = deserialize_rmr_file(proposed_rmr)
    except:
        rmr_are_valid_json = False
        print("Proposed RMR is not a valid JSON file")

    if not rmr_are_valid_json:
        print("")
        return
    else:
        print("----------------------------------")
        print("RUNNING RULE EVALUATIONS...")
        print("  Section 6...")
        print("  Section 12...")
        print("  Section 15...")

        report = evaluate_all_rules(user_rmr_obj, baseline_rmr_obj, proposed_rmr_obj)
        
        print("")
        print("RULE EVALUATIONS COMPLETE.")
        print("----------------------------------")
        print("")
        

        # Example - Print a final compliance report
        # [We'll actually most likely save a data file here and report occurs from separate CLI command]
        #write_json_report(report)
        #print_json_report(report)
        #write_rule_evaluation_report(report)
        #print_rule_report(report)
        print_summary_report(report)

        print("")
        print("PROJECT TESTING WORKFLOW COMPLETE.")



    # # Validate the rmrs against the schema and other high-level checks
    # user_validation = validate_rmr(user_rmr_obj)
    # if user_validation["passed"] is not True:
    #     print("User RMR is " + user_validation["error"])
    #
    # baseline_validation = validate_rmr(baseline_rmr_obj)
    # if baseline_validation["passed"] is not True:
    #     print("Baseline RMR is " + baseline_validation["error"])
    #
    # proposed_validation = validate_rmr(proposed_rmr_obj)
    # if proposed_validation["passed"] is not True:
    #     print("Proposed RMR is " + proposed_validation["error"])
    #
    # print("")
    #
    # if user_validation["passed"] and baseline_validation["passed"] and proposed_validation["passed"]:
    #     print("Processing rules...")
    #     print("")
    #     evaluate_all_rules(user_rmr_obj, baseline_rmr_obj, proposed_rmr_obj)
    #     print("Rules completed.")
    #     print("")


# Run Rule Tests
short_help_text = "Validate RCT by running Rule Tests."
help_text = short_help_text
@cli.command("run_software_tests", short_help=short_help_text, help=help_text, hidden=True)
def run_software_tests():
    print("")
    print("*****************************************************************")
    print("ASHRAE Std 229P Ruleset Checking Tool")
    print("Software Testing Workflow")
    print("Ruleset: ASHRAE 90.1-2019 Performance Rating Method (Appendix G)")
    print("*****************************************************************")
    print("")

    test_outcomes = {}
    try:
        print("----------------------------------")
        print("RUNNING RULE TESTS...")
        test_outcomes['lighting'] = run_section_tests("lighting_tests.json")
        test_outcomes['receptacles'] = run_section_tests("receptacle_tests.json")
        test_outcomes['transformers'] = run_section_tests("transformer_tests.json")
        print("")
        print("RULE TESTS COMPLETE.")
        print("----------------------------------")
        print("")
        print_software_summary_report(test_outcomes)

    except:
        print("Rule Tests failed.")

    print("")
    print("SOFTWARE TESTING WORKFLOW COMPLETE.")
    print("")


if __name__ == "__main__":
    cli()
