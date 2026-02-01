# nornir_rich

## My branch (per_panel_var)

Adds a few extra options to the *print_result* method:

- *print_empty_task* (default True): If set to *False* will not print a task if the task *result* is *Null* or an empty string (*""*)
- *per_panel_var* (default False): If set to *True* puts each *result var* in its own *rich panel*. If the var is a dictionary rather than having var name as the panel title uses key for each dictionary item (all displayed in the one panel)

```python
print_result(
    results,
    vars=["name", "result"],
    print_empty_task=False,
    per_panel_var=True,
)
```

<img width="1491" height="743" alt="Image" src="https://github.com/user-attachments/assets/08cfb946-479f-464e-81a8-45b4efb2a5b2" />

To install this branch:

```bash
pip install git+https://github.com/sjhloco/nornir_rich@per_panel_var
```

## Install

```bash
pip install nornir-rich
```

## Usage

Features

- Print functions
  - `print_result`
  - `print_failed_hosts`
  - `print_inventory`
- Processors
  - `progressbar`


### Print example

```python
from nornir_rich.functions import print_result

results = nr.run(
    task=hello_world
)

print_result(results)
print_result(results, vars=["diff", "result", "name", "exception", "severity_level"])
```

### Progress bar example

```python
from time import sleep
from nornir_rich.progress_bar import RichProgressBar


def random_sleep(task: Task) -> Result:
    delay = randrange(10)
    sleep(delay)
    return Result(host=task.host, result=f"{delay} seconds delay")


nr_with_processors = nr.with_processors([RichProgressBar()])
result = nr_with_processors.run(task=random_sleep)
```


## Images

### Print Inventory

![Print inventory](docs/imgs/print_inventory.png)

### Print Result

![Print Result](docs/imgs/print_result.png)

### Progress Bar

![Progress Bar](docs/imgs/progressbar.png)


More [examples](docs/imgs/print_functions.ipynb)
