import os
import sys
import uuid
import asyncio
import contextlib
import subprocess

from pytest_simbind import SimbindCollector, dto as simbind_dto

_tests_root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
_assets_path = os.path.join(_tests_root_path, "assets")
_example_tests_path = os.path.join(_assets_path, "example_tests")
_sil_model_path = os.path.join(_assets_path, "model-6.3-py3-none-linux_x86_64.whl")
_mock_model_path = os.path.join(_assets_path, "model-6.3+mock-py3-none-any.whl")


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


async def collect_data(classifier_tuple_lst: list[tuple[str, uuid.UUID]]) -> list[simbind_dto.TestUpdateDto]:
    def classifier(test_case: simbind_dto.TestCaseInfoDto):
        for test_name, test_id in classifier_tuple_lst:
            if test_case.function_name == test_name:
                return test_id
        return None

    collector = SimbindCollector(_example_tests_path, classifier)

    test_data: list[simbind_dto.TestUpdateDto] = []
    async for msg in collector.start():
        test_data.append(msg)
    return test_data


async def test_no_selection():
    def classifier(_: simbind_dto.TestCaseInfoDto):
        return None

    collector = SimbindCollector(_example_tests_path, classifier)

    async for _ in collector.start():
        assert False, "No messages expected"


async def test_1_1_1_non_zero_input_selected():
    test_id = uuid.uuid4()
    test_data = await collect_data([("test_1_1_1_non_zero_input", test_id)])

    assert len(test_data) == 2

    assert test_data[0].test_id == test_id
    assert test_data[0].progress == simbind_dto.TestProgressEnum.RUNNING
    assert test_data[0].data.timestamp == 0
    assert any([val != 0 for val in test_data[0].data.inputs.values()])
    assert test_data[0].status is None

    assert test_data[1].test_id == test_id
    assert test_data[1].progress == simbind_dto.TestProgressEnum.FINISHED
    assert test_data[1].status.state == simbind_dto.TestStateEnum.SUCCEED
    assert test_data[1].data is None


async def test_1_1_2_ten_steps_selected():
    test_id = uuid.uuid4()
    test_data = await collect_data([("test_1_1_2_ten_steps", test_id)])

    assert len(test_data) == 12

    assert test_data[0].test_id == test_id
    assert test_data[0].progress == simbind_dto.TestProgressEnum.RUNNING
    assert test_data[0].data.timestamp == 0
    assert any([val != 0 for val in test_data[0].data.inputs.values()])
    assert test_data[0].status is None

    assert len([update for update in test_data if update.data and update.data.timestamp == 0]) == 1

    assert test_data[11].test_id == test_id
    assert test_data[11].progress == simbind_dto.TestProgressEnum.FINISHED
    assert test_data[11].status.state == simbind_dto.TestStateEnum.SUCCEED
    assert test_data[11].data is None


async def test_module_1_1_selected():
    test1_id = uuid.uuid4()
    test2_id = uuid.uuid4()
    test_data = await collect_data([
        ("test_1_1_1_non_zero_input", test1_id),
        ("test_1_1_2_ten_steps", test2_id),
    ])

    assert len(test_data) == 14

    test1_data = [data for data in test_data if data.test_id == test1_id]
    test2_data = [data for data in test_data if data.test_id == test2_id]

    assert len(test1_data) == 2
    assert len(test2_data) == 12
    assert len([
        update for update in test1_data if
        update.progress == simbind_dto.TestProgressEnum.FINISHED and update.status.state == simbind_dto.TestStateEnum.SUCCEED
    ]) == 1
    assert len([
        update for update in test2_data if
        update.progress == simbind_dto.TestProgressEnum.FINISHED and update.status.state == simbind_dto.TestStateEnum.SUCCEED
    ]) == 1


async def test_2_1_1_single_log_selected():
    test_id = uuid.uuid4()
    test_data = await collect_data([
        ("test_2_1_1_single_log", test_id)
    ])

    assert len(test_data) == 2
    assert len(test_data[0].data.log_messages) == 1


async def test_2_1_2_ten_logs_selected():
    test_id = uuid.uuid4()
    test_data = await collect_data([
        ("test_2_1_2_ten_logs", test_id)
    ])

    assert len(test_data) == 12
    for idx in range(10):
        assert len(test_data[idx].data.log_messages) == 1
    assert len(test_data[10].data.log_messages) == 0
    assert test_data[11].data is None


async def test_21_1_1_realistic_selected():
    test_id = uuid.uuid4()
    test_data = await collect_data([
        ("test_21_1_1_realistic", test_id)
    ])

    assert test_data[-2].data.timestamp >= 0.1
    assert test_data[-1].progress == simbind_dto.TestProgressEnum.FINISHED
    assert test_data[-1].status.state == simbind_dto.TestStateEnum.FAILED
    assert test_data[-1].data is None
    assert test_data[-1].status.internal_error is None
    assert test_data[-1].status.fail_details is not None
    assert test_data[-1].status.fail_details.line_number == 15
    assert test_data[-1].status.fail_details.file_location == "package2/package21/module_21_1_test.py"
    assert test_data[-1].status.fail_details.text == "Something went wrong"


async def test_21_1_2_exception():
    test_id = uuid.uuid4()
    test_data = await collect_data([
        ("test_21_1_2_exception", test_id)
    ])

    assert test_data[-1].progress == simbind_dto.TestProgressEnum.FINISHED
    assert test_data[-1].status.state == simbind_dto.TestStateEnum.FAILED
    assert test_data[-1].data is None
    assert test_data[-1].status.internal_error is None
    assert test_data[-1].status.fail_details is not None
    assert test_data[-1].status.fail_details.line_number == 20
    assert test_data[-1].status.fail_details.file_location == "package2/package21/module_21_1_test.py"
    assert test_data[-1].status.fail_details.text == "Something went wrong"


async def test_all_selected():
    def classifier(_: simbind_dto.TestCaseInfoDto):
        return str(uuid.uuid4())

    collector = SimbindCollector(_example_tests_path, classifier)

    test_data: list[simbind_dto.TestUpdateDto] = []
    async for msg in collector.start():
        test_data.append(msg)

    assert len(set([update.test_id for update in test_data])) == 6
    assert len([update for update in test_data if update.progress == simbind_dto.TestProgressEnum.FINISHED]) == 6
    assert len([
        update for update in test_data if
        update.progress == simbind_dto.TestProgressEnum.FINISHED and
        update.status.state == simbind_dto.TestStateEnum.FAILED
    ]) == 2


async def tests_stack():
    for model_path in [_sil_model_path, _mock_model_path]:
        with install_model(model_path):
            await test_no_selection()
            await test_1_1_1_non_zero_input_selected()
            await test_1_1_2_ten_steps_selected()
            await test_module_1_1_selected()
            await test_2_1_1_single_log_selected()
            await test_2_1_2_ten_logs_selected()
            await test_21_1_1_realistic_selected()
            await test_21_1_2_exception()
            await test_all_selected()


if __name__ == '__main__':
    asyncio.run(tests_stack())
