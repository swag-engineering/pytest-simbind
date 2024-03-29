# pytest-simbind

pytest-simbind is [pytest](https://docs.pytest.org/en/latest/contents.html) plugin that
facilitates [SiL testing](https://de.wikipedia.org/wiki/Software_in_the_Loop)
of [Simbind](https://github.com/swag-engineering/simbind-cli) objects. For a ready-to-use service solution refer
to [Simtest](https://github.com/swag-engineering/simtest).

Specially, pytest-simbind allows to overcome main limitation
of [Simbind](https://github.com/swag-engineering/simbind-cli) generated objects:
> Due to the nature of binding technology you can instantiate Model class only once within a single process, all
> consequent instances will have the same state(time, input, and output props) as the first instance. If you need to
> instantiate multiple objects we recommend doing it in separate processes.

The core plugin integrates with _pytest_ in an almost seamless manner, requiring only two simple steps from the user:

- Decorate Simbind model fixture with _@pytest_simbind.fixture_. This helps _pytest_ to keep track on _Simbind_ fixture
  lifecycle and is mandatory if you need to use [plugin's API](#using-api).
- Mark tests with _@pytest.mark.simbind_ to make it run in separate process.

```python
import pytest, pytest_simbind

from model import Model


@pytest_simbind.fixture
def model():
    return Model()


@pytest.mark.simbind
def test_something(model: Model):
    ...
```

# Installation

To install pytest-simbind run:

```bash
$ pip install pytest-simbind
```

# Requirements

You will need Python 3.10+ to run plugin. Additionally, plugin inherits some requirements
from [Simbind](https://github.com/swag-engineering/simbind-cli) generated objects: while you can test
your Mock model under any operational system, SiL model requires Linux! To learn more about Mock and SiL packages
structure and usage, refer
to [Simbind Wiki](https://github.com/swag-engineering/simbind-cli/wiki/Python-Package-Structure).

# Using API

pytest-simbind provides asynchronous API to:

- dynamically select and run tests
- collect [Simbind](https://github.com/swag-engineering/simbind-cli) model's data, test logs and fail reports.

Here is basic example on how to use API:

```python
from pytest_simbind import SimbindCollector, dto as simbind_dto


def classifier(test_case: simbind_dto.TestCaseInfoDto) -> int | str | None:
    return test_case.node_id  # to select all the tests


collector = SimbindCollector(path_to_tests_root, classifier)

async for msg in collector.start():
    ...
```

The [
_SimbindCollector_](https://github.com/swag-engineering/pytest-simbind/blob/master/pytest_simbind/SimbindCollector.py#L17)
requires path to the root directory of the tests and _classifier_ callback function. This function is invoked for each
discovered test. The return value of the _classifier_ will be used as an _id_ to tag the collected data from the test.
If _classifier_ returns _None_, test will be deselected from the execution run.

We encourage you to explore [_dto_](https://github.com/swag-engineering/pytest-simbind/tree/master/pytest_simbind/dto)
structures to better understand how to interact with the plugin. [
_TestCaseInfoDto_](https://github.com/swag-engineering/pytest-simbind/blob/master/pytest_simbind/dto/TestCaseInfoDto.py)
and [
_TestUpdateDto_](https://github.com/swag-engineering/pytest-simbind/blob/master/pytest_simbind/dto/TestUpdateDto.py)
could be a good start!

[Simtest](https://github.com/swag-engineering/simtest) can be also used as an example and source of code snippets on how
to interact with the plugin's API!