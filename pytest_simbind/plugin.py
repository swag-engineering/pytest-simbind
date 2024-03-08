from .SimbindCorePlugin import SimbindCorePlugin


def pytest_configure(config):
    config.pluginmanager.register(SimbindCorePlugin(), "pytest_simbind_core")
