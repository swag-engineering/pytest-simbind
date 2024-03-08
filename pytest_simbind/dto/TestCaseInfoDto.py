from dataclasses import dataclass


@dataclass(frozen=True)
class TestCaseInfoDto:
    __test__ = False
    node_id: str
    function_name: str
    module_name: str
    package_path: str
