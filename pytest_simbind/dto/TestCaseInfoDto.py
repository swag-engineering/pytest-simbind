from dataclasses import dataclass


@dataclass(frozen=True)
class TestCaseInfoDto:
    node_id: str
    function_name: str
    module_name: str
    package_path: str
