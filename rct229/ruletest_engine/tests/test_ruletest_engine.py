from rct229.ruletest_engine.ruletest_engine import (
    run_lighting_tests,
    run_receptacle_tests,
    run_transformer_tests,
)


def test_run_transformer_tests():

    assert run_transformer_tests()


def test_run_lighting_tests():

    assert run_lighting_tests()


def test_run_receptacle_tests():

    assert run_receptacle_tests()
