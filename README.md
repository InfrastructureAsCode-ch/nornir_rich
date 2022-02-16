# nornir_rich

## Install

```bash
pip install nornir-rich
```

## Usage

print functions with rich

- `print_result`
- `print_failed_hosts`
- `print_inventory`

```python
from nornir_rich.functions import print_result

results = nr.run(
    task=hello_world
)

print_result(results)
print_result(results, vars=["diff", "result", "name", "exception", "severity_level"])
```

## Images

### Print Inventory

![Print inventory](docs/print_inventory.png)

### Print Result

![Print Result](docs/print_result.png)


More [examples](docs/print_functions.ipynb)