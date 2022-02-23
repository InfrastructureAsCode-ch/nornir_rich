import threading
from typing import Optional
from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult, Task
from rich.progress import (
    Progress,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    Table,
    Live,
)
from rich.panel import Panel
from rich.protocol import rich_cast


class RichProgressBar:
    def __init__(
        self,
        description: str = "[progress.description]{task.description}",
        progress_percentage: str = "[progress.percentage]{task.completed:>5.0f}/{task.total}",
        total_hosts: Optional[int] = None,
    ) -> None:
        self.lock = threading.Lock()
        self.total_hosts = total_hosts

        self.progress_total = Progress(
            description,
            BarColumn(bar_width=80),
            progress_percentage,
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        )
        self.progress_status = Progress(
            description,
            BarColumn(bar_width=96),
            progress_percentage,
        )
        self.progress_running_tasks = Progress(
            description,
            BarColumn(bar_width=80),
            progress_percentage,
        )

        self.overall_progress_table = Table.grid()
        self.overall_progress_table.add_row(self.progress_total)
        self.progress_table = Table.grid()
        self.progress_table.add_row(
            Panel.fit(
                self.overall_progress_table,
                title="Overall Progress",
                border_style="green",
                padding=(0, 2),
            )
        )
        self.progress_table.add_row(
            Panel.fit(
                self.progress_status,
                title="Task Exit Status",
                border_style="yellow",
                padding=(0, 2),
            )
        )
        self.progress_live = Live(self.progress_table, refresh_per_second=10)

    def task_started(self, task: Task) -> None:
        hosts = (
            self.total_hosts if self.total_hosts else len(task.nornir.inventory.hosts)
        )
        workers = getattr(task.nornir.runner, "num_workers", 1)
        if hosts < workers:
            self.concurrent_count = hosts
        else:
            self.concurrent_count = workers
        self.total_hosts = hosts

        self.successful = self.progress_status.add_task(
            "[green]Successful:", total=self.total_hosts
        )
        self.changed = self.progress_status.add_task(
            "[orange3]Changed:", total=self.total_hosts
        )
        self.error = self.progress_status.add_task(
            "[red]Failed:", total=self.total_hosts
        )

        self.total = self.progress_total.add_task(
            "[cyan]Completed: ", total=self.total_hosts
        )
        self.running_concurrent_bar = self.progress_running_tasks.add_task(
            "[yellow]Concurrent:", total=self.concurrent_count
        )
        self.overall_progress_table.add_row(self.progress_running_tasks)

        self.progress_live.start()

    def task_completed(self, task: Task, result: AggregatedResult) -> None:
        self.progress_live.stop()

    def task_instance_started(self, task: Task, host: Host) -> None:
        with self.lock:
            self.progress_running_tasks.update(self.running_concurrent_bar, advance=1)

    def task_instance_completed(
        self, task: Task, host: Host, results: MultiResult
    ) -> None:
        with self.lock:
            self.progress_running_tasks.update(self.running_concurrent_bar, advance=-1)
            self.progress_total.update(self.total, advance=1)
            self.progress_status.update(
                self.error if results.failed else self.successful, advance=1
            )
            if results.changed:
                self.progress_status.update(self.changed, advance=1)

    def subtask_instance_started(self, task: Task, host: Host) -> None:
        ...

    def subtask_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        ...
