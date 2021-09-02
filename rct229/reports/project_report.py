import json
import os

from rct229.reports.utils import aggregate_outcomes
from rct229.utils.file import save_text_file
from rct229.utils.json_utils import save_json


def write_json_report(report):
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "examples"
    )
    filename = "project_testing_report.json"
    save_json(report, path, filename)


def write_rule_evaluation_report(report):
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "examples"
    )
    filename = "rule_evaluation.log"

    outcomes = report["outcomes"]

    report_str = ""
    for outcome in outcomes:
        report_str += (
            "--------------------------------------------------------------------\n"
        )
        report_str += f"Rule: {str(outcome['id'])}\n"
        report_str += f"Description: {str(outcome['description'])}\n"
        report_str += f"RMR context: {str(outcome['rmr_context'])}\n"
        report_str += f"Rule result: {str(outcome['result'])}\n"
        report_str += (
            "--------------------------------------------------------------------\n"
        )

    save_text_file(report_str, path, filename)


def print_json_report(report):
    print(json.dumps(report, indent=2))


def print_rule_report(report):
    outcomes = report["outcomes"]
    for outcome in outcomes:
        print("--------------------------------------------------------------------")
        print(f"Rule: {str(outcome['id'])}")
        print(f"Description: {str(outcome['description'])}")
        print(f"RMR context: {str(outcome['rmr_context'])}")
        # print(f"Element context: {str(outcome['element_context'])}")
        # print(f"Applicable: {str(outcome['applicable'])}")
        # print(f"Manual check required: {str(outcome['manual_check_required'])}")
        # print(f"Rule passed: {str(outcome['rule_passed'])}")
        print(f"Rule result: {str(outcome['result'])}")
        print("--------------------------------------------------------------------")


def print_summary_report(report):
    invalid_rmrs = report["invalid_rmrs"]
    if invalid_rmrs:
        print("----------------------------------")
        print(f"Invalid RMRs: {str(invalid_rmrs)}")
    else:
        outcomes = report["outcomes"]
        summary_dict = aggregate_outcomes(outcomes)

        print("----------------------------------")
        print("PROJECT TESTING SUMMARY")
        print("----------------------------------")
        print("")
        print("Totals")
        print(f"  Rules: {len(outcomes)}")
        print(f"  Rule Evaluations: {summary_dict['number_evaluations']}")
        print("")
        print("Rule Evaluations")
        print(f"  Passed: {summary_dict['number_passed']}")
        print(f"  Failed: {summary_dict['number_failed']}")
        print(f"  Missing Context: {summary_dict['number_missing_context']}")
        print(f"  Not Applicable: {summary_dict['number_not_applicable']}")
        print(
            f"  Manual Check Required: {summary_dict['number_manual_check_required']}"
        )
        print("")
        print("----------------------------------")
