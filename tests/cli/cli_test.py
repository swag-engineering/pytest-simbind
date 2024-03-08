import multiprocessing

import pytest
from _pytest.pytester import Pytester


@pytest.mark.parametrize("model_selector", ["sil", "mock"], indirect=True)
def test_no_mark_error(pytester, model_selector):
    pytester.makepyfile("""
        import pytest
        
        import pytest_simbind

        @pytest_simbind.fixture
        def model():
            return None

        def test_simbind_fixture(model):
            pass
    """)
    pytester.makeconftest("""
        pytest_plugins = ["pytest_simbind.plugin"]
    """)
    result = pytester.runpytest()
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*Simbind fixture is used within parent process.*"])


@pytest.mark.parametrize("model_selector", ["sil", "mock"], indirect=True)
def test_valid_mark(pytester, model_selector):
    pytester.makepyfile("""
        import pytest

        import pytest_simbind

        @pytest_simbind.fixture
        def model():
            return None
        
        @pytest.mark.simbind
        def test_simbind_fixture(model):
            pass
    """)
    pytester.makeconftest("""
        pytest_plugins = ["pytest_simbind.plugin"]
    """)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize("model_selector", ["sil", "mock"], indirect=True)
def test_valid_mark_with_model(pytester, model_selector):
    pytester.makepyfile("""
        import pytest

        import pytest_simbind
        
        from model import Model

        @pytest_simbind.fixture
        def model():
            return Model()

        @pytest.mark.simbind
        def test_simbind_fixture(model):
            assert model.time == 0
    """)
    pytester.makeconftest("""
        pytest_plugins = ["pytest_simbind.plugin"]
    """)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize("model_selector", ["sil"], indirect=True)
def test_invalid_isolation(pytester, model_selector):
    def execute(outcomes_queue: multiprocessing.Queue, pytester_obj: Pytester):
        result = pytester_obj.runpytest()
        outcomes_queue.put(result.parseoutcomes())

    pytester.makepyfile("""
        import pytest

        from model import Model

        @pytest.fixture
        def model():
            return Model()

        def test_1(model):
            assert model.time == 0
            model.step()

        def test_2(model):
            assert model.time == 0
            model.step()
    """)
    queue = multiprocessing.Queue(-1)
    p = multiprocessing.Process(target=execute, args=(queue, pytester))
    p.start()
    p.join()
    outcomes = queue.get()
    assert outcomes == {'failed': 1, 'passed': 1}


@pytest.mark.parametrize("model_selector", ["sil"], indirect=True)
def test_valid_isolation(pytester, model_selector):
    pytester.makepyfile("""
        import pytest
        
        import pytest_simbind

        from model import Model

        @pytest_simbind.fixture
        def model():
            return Model()

        @pytest.mark.simbind
        def test_1(model):
            assert model.time == 0
            model.step()

        @pytest.mark.simbind
        def test_2(model):
            assert model.time == 0
            model.step()
    """)
    pytester.makeconftest("""
        pytest_plugins = ["pytest_simbind.plugin"]
    """)
    result = pytester.runpytest()
    result.assert_outcomes(passed=2)
