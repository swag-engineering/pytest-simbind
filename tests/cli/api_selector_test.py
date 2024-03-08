import pytest


@pytest.mark.parametrize("model_selector", ["mock"], indirect=True)
def test_all_tests_deselected(pytester, model_selector, example_tests_path):
    pytester.makepyfile("""
        import pytest

        import pytest_simbind
        from model import Model

        @pytest_simbind.fixture
        def model():
            return Model()
        
        @pytest.mark.simbind
        def test_one(model):
            pass
        
        @pytest.mark.simbind
        def test_two(model):
            pass
    """)
    pytester.makeconftest(f"""
    import pytest

    from pytest_simbind import SimbindCollector, TestCaseInfoDto
    
    def empty_classifier(_: TestCaseInfoDto):
        return None
    
    def pytest_configure(config):
        config.pluginmanager.register(
            SimbindCollector("{example_tests_path}", empty_classifier),
            "pytest_simbind_collector"
        )
    """)
    result = pytester.runpytest()
    result.assert_outcomes(deselected=2)


@pytest.mark.parametrize("model_selector", ["mock"], indirect=True)
def test_one_selected(pytester, model_selector, example_tests_path):
    pytester.makepyfile("""
        import pytest

        import pytest_simbind
        from model import Model

        @pytest_simbind.fixture
        def model():
            return Model()

        @pytest.mark.simbind
        def test_one(model):
            pass

        @pytest.mark.simbind
        def test_two(model):
            pass
    """)
    pytester.makeconftest(f"""
    import pytest

    from pytest_simbind import SimbindCollector, TestCaseInfoDto

    def classifier(test_case: TestCaseInfoDto):
        if test_case.function_name == "test_one":
            return "test_one"
        else:
            return None

    def pytest_configure(config):
        config.pluginmanager.register(
            SimbindCollector("{example_tests_path}", classifier),
            "pytest_simbind_collector"
        )
    """)
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1, deselected=1)
    result.stdout.fnmatch_lines("*test_one PASSED*")
    result.stdout.no_fnmatch_line("*test_two*")


@pytest.mark.parametrize("model_selector", ["mock"], indirect=True)
def test_both_selected(pytester, model_selector, example_tests_path):
    pytester.makepyfile("""
        import pytest

        import pytest_simbind
        from model import Model

        @pytest_simbind.fixture
        def model():
            return Model()

        @pytest.mark.simbind
        def test_one(model):
            pass

        @pytest.mark.simbind
        def test_two(model):
            assert False
    """)
    pytester.makeconftest(f"""
    import pytest

    from pytest_simbind import SimbindCollector, TestCaseInfoDto

    def classifier(test_case: TestCaseInfoDto):
        return test_case.function_name

    def pytest_configure(config):
        config.pluginmanager.register(
            SimbindCollector("{example_tests_path}", classifier),
            "pytest_simbind_collector"
        )
    """)
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines("*test_one PASSED*")
    result.stdout.fnmatch_lines("*test_two FAILED*")
