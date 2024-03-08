__test__ = False

import asyncio
import contextlib
import subprocess

import os
import sys
import uuid

_tests_root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
_assets_path = os.path.join(_tests_root_path, "assets")
_example_tests_path = os.path.join(_assets_path, "example_tests")
_sil_model_path = os.path.join(_assets_path, "model-6.3-py3-none-linux_x86_64.whl")
_mock_model_path = os.path.join(_assets_path, "model-6.3+mock-py3-none-any.whl")

_project_root_path = os.path.dirname(_tests_root_path)
sys.path.append(_project_root_path)
from pytest_simbind import SimbindCollector, dto


@contextlib.contextmanager
def install_model(model_path: str):
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--force-reinstall", "--no-index", model_path],
        check=True,
        stdout=subprocess.DEVNULL
    )
    try:
        yield
    finally:
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", "model"],
            check=True,
            stdout=subprocess.DEVNULL
        )


async def test_no_selection():
    def classifier(_: dto.TestCaseInfoDto):
        return None

    collector = SimbindCollector(_example_tests_path, classifier)

    async for _ in collector.start():
        assert False, "No messages expected"


async def single_test_selected():
    test_id = uuid.uuid4()

    def classifier(test_case: dto.TestCaseInfoDto):
        return test_id if test_case.function_name == "test_1_1_1_non_zero_input" else None

    collector = SimbindCollector(_example_tests_path, classifier)

    test_data: list[dto.TestUpdateDto] = []
    async for msg in collector.start():
        test_data.append(msg)
    
    assert len(test_data) == 2

    assert test_data[0].test_id == test_id
    assert test_data[0].progress == dto.TestProgressDto.RUNNING
    assert test_data[0].data.timestamp == 0
    assert any([val != 0 for val in test_data[0].data.inputs.values()])
    assert test_data[0].status is None

    assert test_data[1].test_id == test_id
    assert test_data[1].progress == dto.TestProgressDto.FINISHED
    assert test_data[1].status.state == dto.TestStateEnum.SUCCEED
    assert test_data[1].data is None


async def tests_stack():
    for model_path in [_sil_model_path, _mock_model_path]:
        with install_model(model_path):
            await test_no_selection()
            await single_test_selected()


if __name__ == '__main__':
    asyncio.run(tests_stack())
