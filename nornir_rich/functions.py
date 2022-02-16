import logging
import threading
from typing import Any, Iterable, List, Optional, Union, Dict
from nornir.core import Nornir, inventory
from nornir.core.inventory import Inventory

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
        columns_settings: Dict[str, Any] = dict(),
        padding: PaddingDimensions = None,
        expand: bool = False,
        equal: bool = True,
        vars: List[str] = None,
        severity_level: int = 0,
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

    def print_multi_result(self, result: MultiResult, host: str = "HOST") -> Panel:
        """
        Render all task results in a MultiResult

        Arguments:
          result: MultiResult to render
          host: Hostname

        Return:
          rich.panel.Panel
        """
        results: List[Union[Panel, None]] = [
            self.print_result(r)
            for r in result
            if r.severity_level >= self.severity_level
        ]
        columns = [p for p in results if p is not None] or None
        panel = Panel(
            Columns(columns, **self.columns_settings),
            title=f"{host} | {result.name}",
            style="red" if result.failed else "green",
        )
        return panel

    def print_result(self, result: Result) -> Union[Panel, None]:
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
            result.result if result.result is not None else "",
            title=result.name,
            style="red" if result.failed else "green",
        )

    def print_scopes(self, scopes: Dict[str, Any]) -> Columns:
        if self.vars:
            columns = [render_scope({k: v for k, v in map.items() if k in self.vars}, title=name) for name, map in scopes.items()]
        else:
            columns = [render_scope(map, title=name) for name, map in scopes.items()]
        return Columns(
            columns,
            **self.columns_settings,
        )


def print_result(
    result: Union[Result, MultiResult, AggregatedResult],
    vars: List[str] = None,
    failed: bool = False,
    severity_level: int = logging.INFO,
    columns_settings: Dict[str, Any] = dict(),
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
    columns_settings: Dict[str, Any] = dict(),
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


def print_inventory(
    inventory: Union[Inventory, Nornir],
    vars: List[str] = None,
    failed: bool = False,
    severity_level: int = logging.INFO,
    columns_settings: Dict[str, Any] = dict(),
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

    if isinstance(inventory, Nornir):
        inventory = inventory.inventory
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
        print(rh.print_scopes(inventory.hosts))
    finally:
        LOCK.release()
