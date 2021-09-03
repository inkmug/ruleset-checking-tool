def print_summary_report(report):
    # Aggregate number of tests
    number_tests = report['lighting']['number_tests']
    number_tests += report['receptacles']['number_tests']
    number_tests += report['transformers']['number_tests']

    # Aggregate number of passing
    number_passing_tests = report['lighting']['number_passing_tests']
    number_passing_tests += report['receptacles']['number_passing_tests']
    number_passing_tests += report['transformers']['number_passing_tests']

    # Aggregate number of failing
    number_failing_tests = report['lighting']['number_failing_tests']
    number_failing_tests += report['receptacles']['number_failing_tests']
    number_failing_tests += report['transformers']['number_failing_tests']

    # Aggregate number of missing rules
    number_missing_rules = report['lighting']['number_missing_rules']
    number_missing_rules += report['receptacles']['number_missing_rules']
    number_missing_rules += report['transformers']['number_missing_rules']


    #outcomes = report["outcomes"]
    #summary_dict = aggregate_outcomes(outcomes)

    print("----------------------------------")
    print("SOFTWARE TESTING SUMMARY")
    print("----------------------------------")
    print("Totals")
    print(f"  Tests: {number_tests}")
    #print(f"  Rule Evaluations: {summary_dict['number_evaluations']}")
    print("")
    print("Rule Tests")
    print(f"  Passed: {number_passing_tests}")
    print(f"  Failed: {number_failing_tests}")
    print(f"  Missing Rules: {number_missing_rules}")
    print("----------------------------------")
