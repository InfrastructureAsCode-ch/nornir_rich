import logging
import threading
from typing import List, Union

from nornir.core.task import AggregatedResult, MultiResult, Result

from rich import print
from rich.columns import Columns
from rich.panel import Panel
from rich.scope import render_scope
from rich.padding import PaddingDimensions


LOCK = threading.Lock()


class RichHelper:
    """
    Helper object for rendering rich columns and panels

    Arguments:
      columns_settings: Settings passed to `rich.columns.Columns` object
      padding: Optional padding around cells. Defaults to (0, 1).
      expand: Expand columns to full width. Defaults to False.
      equal: Equal sized columns. Defaults to False
      vars: Which attributes you want to print
      severity_level: Print only errors with this severity level or higher
      failed: if ``True`` assume the task failed
    """

    def __init__(
        self,
        columns_settings: dict = dict(),
        padding: PaddingDimensions = None,
        expand: bool = False,
        equal: bool = True,
        vars: List[str] = None,
        severity_level: int = None,
        failed: bool = None,
    ) -> None:
        self.columns_settings = columns_settings
        self.columns_settings["expand"] = expand
        self.columns_settings["equal"] = equal
        if padding:
            self.columns_settings["padding"] = padding
        self.vars = vars
        self.severity_level = severity_level
        self.failed = failed

    def print_aggregated_result(self, result: AggregatedResult) -> Panel:
        """
        Render all task results per each host in AggregatedResult

        Arguments:
          result: AggregatedResult to render

        Return:
          rich.panel.Panel
        """
        mulit_results = [
            self.print_multi_result(result=mulit_result, host=host)
            for host, mulit_result in result.items()
        ]
        columns = Columns(mulit_results, **self.columns_settings)
        panel = Panel(
            columns, title=result.name, style="red" if result.failed else "green"
        )
        return panel

    def print_multi_result(self, result: MultiResult, host: str) -> Panel:
        """
        Render all task results in a MultiResult

        Arguments:
          result: MultiResult to render
          host: Hostname

        Return:
          rich.panel.Panel
        """
        results = [
            self.print_result(r)
            for r in result
            if r.severity_level >= self.severity_level
        ]
        panel = Panel(
            Columns(results, **self.columns_settings),
            title=f"{host} | {result.name}",
            style="red" if result.failed else "green",
        )
        return panel

    def print_result(self, result: Result) -> Panel:
        """
        Render individual task result

        Arguments:
          result: Individual result to render

        Return:
          rich.panel.Panel
        """
        if result.severity_level < self.severity_level:
            return None
        if self.vars:
            return Panel(
                render_scope({x: getattr(result, x) for x in self.vars}),
                title=result.name,
                style="red" if result.failed else "green",
            )
        return Panel(
            result.result, title=result.name, style="red" if result.failed else "green",
        )


def print_result(
    result: Union[Result, MultiResult, AggregatedResult],
    vars: List[str] = None,
    failed: bool = False,
    severity_level: int = logging.INFO,
    columns_settings: dict = dict(),
    padding: PaddingDimensions = None,
    expand: bool = False,
    equal: bool = True,
) -> None:
    """
    Prints an object of type `nornir.core.task.Result` || `nornir.core.task.MultiResult` || `nornir.core.task.AggregatedResult`

    Arguments:
      result: from a previous task
      vars: Which attributes you want to print
      failed: if ``True`` assume the task failed
      severity_level: Print only errors with this severity level or higher
      columns_settings: Settings passed to `rich.columns.Columns` object
      padding: Optional padding around cells. Defaults to (0, 1).
      expand: Expand columns to full width. Defaults to False.
      equal: Equal sized columns. Defaults to False
    """
    LOCK.acquire()
    equal = False if expand else equal
    rh = RichHelper(
        columns_settings=columns_settings,
        padding=padding,
        expand=expand,
        equal=equal,
        vars=vars,
        severity_level=severity_level,
        failed=failed,
    )
    try:
        if isinstance(result, AggregatedResult):
            print(rh.print_aggregated_result(result))
        elif isinstance(result, MultiResult):
            print(rh.print_multi_result(result))
        elif isinstance(result, Result):
            print(rh.print_result(result))
    finally:
        LOCK.release()


def print_failed_hosts(
    result: AggregatedResult,
    vars: List[str] = None,
    failed: bool = False,
    severity_level: int = logging.INFO,
    columns_settings: dict = dict(),
    padding: PaddingDimensions = None,
    expand: bool = False,
    equal: bool = True,
) -> None:
    """
    Prints results of all failed hosts from `nornir.core.task.AggregatedResult`

    Arguments:
      result: from a previous task
      vars: Which attributes you want to print
      failed: if ``True`` assume the task failed
      severity_level: Print only errors with this severity level or higher
      columns_settings: Settings passed to `rich.columns.Columns` object
      padding: Optional padding around cells. Defaults to (0, 1).
      expand: Expand columns to full width. Defaults to False.
      equal: Equal sized columns. Defaults to False
    """
    LOCK.acquire()
    equal = False if expand else equal
    rh = RichHelper(
        columns_settings=columns_settings,
        padding=padding,
        expand=expand,
        equal=equal,
        vars=vars,
        severity_level=severity_level,
        failed=failed,
    )
    try:
        for host, multi_result in result.failed_hosts.items():
            print(rh.print_multi_result(multi_result, host))
    finally:
        LOCK.release()