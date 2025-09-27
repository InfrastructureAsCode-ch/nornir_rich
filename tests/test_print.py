import io
import logging
from typing import Any, Union
import pytest

from rich.console import Console
from rich.panel import Panel

from nornir.core.inventory import Host
from nornir.core.task import Result, MultiResult, AggregatedResult

from nornir_rich.functions import RichHelper


@pytest.fixture
def host_one() -> Host:
    return Host(name="host1", hostname="host1.test", username="user", password="pass")


@pytest.fixture
def result_one(host_one: Host) -> Result:
    return Result(host=host_one, result="Demo result one")


@pytest.fixture
def result_two(host_one: Host) -> Result:
    return Result(
        host=host_one, result="Demo result two", diff="changed 'one' to 'two'"
    )


@pytest.fixture
def result_three(host_one: Host) -> Result:
    return Result(
        host=host_one,
        result="Demo result three\nHas a new line",
        diff="changed 'two' to 'three'\n",
    )


@pytest.fixture
def result_failed_one(host_one: Host) -> Result:
    return Result(host=host_one, result="Demo failed result", failed=True)


@pytest.fixture
def result_failed_two(host_one: Host) -> Result:
    return Result(
        host=host_one,
        result="Second failed result",
        failed=True,
        diff="did not work well",
    )


@pytest.fixture
def multiresult_one(result_one: Result) -> MultiResult:
    mr = MultiResult("MultiResult 1")
    mr.append(result_one)
    return mr


@pytest.fixture
def multiresult_two(result_one: Result, result_two: Result) -> MultiResult:
    mr = MultiResult("MultiResult 2")
    mr.extend([result_one, result_two])
    return mr


@pytest.fixture
def multiresult_three(
    result_one: Result, result_two: Result, result_failed_one: Result
) -> MultiResult:
    mr = MultiResult("MultiResult 3")
    mr.extend([result_one, result_two, result_failed_one])
    return mr


@pytest.fixture
def aggregatedresult_one(multiresult_one: MultiResult) -> AggregatedResult:
    return AggregatedResult(
        name="Aggregated Result 1", **{"host1.test": multiresult_one}
    )


@pytest.fixture
def aggregatedresult_two(
    multiresult_two: MultiResult,
) -> AggregatedResult:
    host_two = Host(
        name="host2", hostname="host2.test", username="user", password="pass"
    )
    mr = MultiResult("MultiResult host 2")
    mr.append(Result(host=host_two, result="Second host"))
    return AggregatedResult(
        name="Aggregated Result 1", **{"host1.test": multiresult_two, "host2.test": mr}
    )


def render(panel: Union[Panel, None], width: int = 50) -> str:
    console = Console(file=io.StringIO(), width=width, legacy_windows=False)
    console.print(panel)
    output: str = console.file.getvalue()  # type: ignore
    print(repr(output))
    print(output)
    return output


@pytest.mark.parametrize(
    "result_name,expected",
    [
        (
            "result_one",
            "╭────────────────────────────────────────────────╮\n│ Demo result one                                │\n╰────────────────────────────────────────────────╯\n",
        ),
        (
            "result_two",
            "╭────────────────────────────────────────────────╮\n│ Demo result two                                │\n╰────────────────────────────────────────────────╯\n",
        ),
    ],
    ids=["result_one", "result_two"],
)
def test_print_result_two(
    result_name: str, expected: str, request: pytest.FixtureRequest
) -> None:
    panel = RichHelper().print_result(request.getfixturevalue(result_name))
    output = render(panel)
    assert output == expected


@pytest.mark.parametrize(
    "result_name,expected",
    [
        (
            "result_one",
            "╭────────────────────────────────────────────────╮\n│ ╭────────────────────────────╮                 │\n│ │   diff = ''                │                 │\n│ │ result = 'Demo result one' │                 │\n│ ╰────────────────────────────╯                 │\n╰────────────────────────────────────────────────╯\n",
        ),
        (
            "result_two",
            "╭────────────────────────────────────────────────╮\n│ ╭───────────────────────────────────╮          │\n│ │   diff = \"changed 'one' to 'two'\" │          │\n│ │ result = 'Demo result two'        │          │\n│ ╰───────────────────────────────────╯          │\n╰────────────────────────────────────────────────╯\n",
        ),
    ],
    ids=["result_one", "result_two"],
)
def test_print_result_one_vars(
    result_name: str, expected: str, request: pytest.FixtureRequest
) -> None:
    panel = RichHelper(vars=["result", "diff"]).print_result(
        request.getfixturevalue(result_name)
    )
    output = render(panel)
    assert output == expected


@pytest.mark.parametrize(
    "result_name,expected",
    [
        (
            "result_one",
            "╭────────────────────────────────────────────────╮\n│ ╭──────────────────────────╮                   │\n│ │   diff =                 │                   │\n│ │ result = Demo result one │                   │\n│ ╰──────────────────────────╯                   │\n╰────────────────────────────────────────────────╯\n",
        ),
        (
            "result_two",
            "╭────────────────────────────────────────────────╮\n│ ╭─────────────────────────────────╮            │\n│ │   diff = changed 'one' to 'two' │            │\n│ │ result = Demo result two        │            │\n│ ╰─────────────────────────────────╯            │\n╰────────────────────────────────────────────────╯\n",
        ),
        (
            "result_three",
            "╭────────────────────────────────────────────────╮\n│ ╭───────────────────────────────────╮          │\n│ │   diff = changed 'two' to 'three' │          │\n│ │ result = Demo result three        │          │\n│ │          Has a new line           │          │\n│ ╰───────────────────────────────────╯          │\n╰────────────────────────────────────────────────╯\n",
        ),
    ],
    ids=["result_one", "result_two", "result_three"],
)
def test_print_result_vars_line_breaks(
    result_name: str, expected: str, request: pytest.FixtureRequest
) -> None:
    panel = RichHelper(vars=["result", "diff"], line_breaks=True).print_result(
        request.getfixturevalue(result_name)
    )
    output = render(panel)
    assert output == expected


@pytest.mark.parametrize(
    "multi_result_name,expected",
    [
        (
            "multiresult_one",
            "╭───────────── HOST | MultiResult 1 ─────────────╮\n│ ╭─────────────────╮                            │\n│ │ Demo result one │                            │\n│ ╰─────────────────╯                            │\n╰────────────────────────────────────────────────╯\n",
        ),
        (
            "multiresult_two",
            "╭───────────── HOST | MultiResult 2 ─────────────╮\n│ ╭─────────────────╮ ╭─────────────────╮        │\n│ │ Demo result one │ │ Demo result two │        │\n│ ╰─────────────────╯ ╰─────────────────╯        │\n╰────────────────────────────────────────────────╯\n",
        ),
        (
            "multiresult_three",
            "╭───────────── HOST | MultiResult 3 ─────────────╮\n│ ╭────────────────────╮ ╭─────────────────╮     │\n│ │ Demo result one    │ │ Demo result two │     │\n│ ╰────────────────────╯ ╰─────────────────╯     │\n│ ╭────────────────────╮                         │\n│ │ Demo failed result │                         │\n│ ╰────────────────────╯                         │\n╰────────────────────────────────────────────────╯\n",
        ),
    ],
    ids=["multiresult_one", "multiresult_two", "multiresult_three"],
)
def test_print_multi_result(
    multi_result_name: str, expected: str, request: pytest.FixtureRequest
) -> None:
    panel = RichHelper().print_multi_result(request.getfixturevalue(multi_result_name))
    output = render(panel)
    assert output == expected


def test_print_multi_result_hostname(multiresult_three: MultiResult) -> None:
    panel = RichHelper().print_multi_result(multiresult_three, host="host1.test")
    output = render(panel)
    expected = "╭────────── host1.test | MultiResult 3 ──────────╮\n│ ╭────────────────────╮ ╭─────────────────╮     │\n│ │ Demo result one    │ │ Demo result two │     │\n│ ╰────────────────────╯ ╰─────────────────╯     │\n│ ╭────────────────────╮                         │\n│ │ Demo failed result │                         │\n│ ╰────────────────────╯                         │\n╰────────────────────────────────────────────────╯\n"
    assert output == expected


@pytest.mark.parametrize(
    "aggregated_result_name,expected",
    [
        (
            "aggregatedresult_one",
            "╭───────────── Aggregated Result 1 ──────────────╮\n│ ╭──────── host1.test | MultiResult 1 ────────╮ │\n│ │ ╭─────────────────╮                        │ │\n│ │ │ Demo result one │                        │ │\n│ │ ╰─────────────────╯                        │ │\n│ ╰────────────────────────────────────────────╯ │\n╰────────────────────────────────────────────────╯\n",
        ),
        (
            "aggregatedresult_two",
            "╭───────────── Aggregated Result 1 ──────────────╮\n│ ╭──────── host1.test | MultiResult 2 ────────╮ │\n│ │ ╭─────────────────╮ ╭─────────────────╮    │ │\n│ │ │ Demo result one │ │ Demo result two │    │ │\n│ │ ╰─────────────────╯ ╰─────────────────╯    │ │\n│ ╰────────────────────────────────────────────╯ │\n│ ╭───── host2.test | MultiResult host 2 ──────╮ │\n│ │ ╭─────────────╮                            │ │\n│ │ │ Second host │                            │ │\n│ │ ╰─────────────╯                            │ │\n│ ╰────────────────────────────────────────────╯ │\n╰────────────────────────────────────────────────╯\n",
        ),
    ],
    ids=["aggregatedresult_one", "aggregatedresult_two"],
)
def test_print_aggregated_result(
    aggregated_result_name: str, expected: str, request: pytest.FixtureRequest
) -> None:
    panel = RichHelper().print_aggregated_result(
        request.getfixturevalue(aggregated_result_name)
    )
    output = render(panel)
    assert output == expected


def test_print_result_severity_level(host_one: Host) -> None:
    result = Result(host=host_one, result="test", severity_level=logging.DEBUG)
    panel = RichHelper(severity_level=logging.ERROR).print_result(result)
    assert panel == None

    mr = MultiResult("Severity Level")
    mr.append(result)
    panel = RichHelper(severity_level=logging.ERROR).print_multi_result(mr)
    output = render(panel)
    expected = "╭──────────── HOST | Severity Level ─────────────╮\n╰────────────────────────────────────────────────╯\n"
    assert output == expected

    mr.append(Result(host=host_one, result="Critical", severity_level=logging.CRITICAL))
    panel = RichHelper(severity_level=logging.ERROR).print_multi_result(mr)
    output = render(panel)
    expected = "╭──────────── HOST | Severity Level ─────────────╮\n│ ╭──────────╮                                   │\n│ │ Critical │                                   │\n│ ╰──────────╯                                   │\n╰────────────────────────────────────────────────╯\n"
    assert output == expected


@pytest.mark.parametrize(
    "result_data,expected",
    [
        ({"a": {"b": "c"}}, "'b':"),
        (["test", 123], "test"),
        (12345, "12345"),
        ("text", "text"),
    ],
    ids=["dict", "list", "int", "str"],
)
def test_result_datatypes(host_one: Host, result_data: Any, expected: str) -> None:
    result = Result(host=host_one, result=result_data)
    panel = RichHelper().print_result(result)
    output = render(panel)
    assert expected in output
