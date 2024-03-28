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


In the nutshell, pytest-simbind allows running each _simbind_ marked test in new process:

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

Notice _@pytest_simbind.fixture_ and _@pytest.mark.simbind_:

- _@pytest_simbind.fixture_ helps _pytest_ to keep track on _Simbind_ fixture lifecycle and is mandatory if you need to
  use [plugin's API](#using-api).
- _@pytest.mark.simbind_ signifies _pytest_ to run specified test in separate process.

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

For more information and examples please refer
to [Wiki](https://github.com/swag-engineering/pytest-simbind/wiki/API-Usage). [Simtest](https://github.com/swag-engineering/simtest)
can also be used as an example and source of code snippets on how to interact with the plugin's API.