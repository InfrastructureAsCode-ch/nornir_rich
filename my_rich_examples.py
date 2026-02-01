from nornir import InitNornir
from nornir.core.task import Result, Task

from nornir_rich.functions import print_result

nr = InitNornir(
    runner={
        "plugin": "threaded",
        "options": {
            "num_workers": 100,
        },
    },
    inventory={
        "plugin": "SimpleInventory",
        "options": {
            "host_file": "tests/demo_inventory/hosts.yaml",
            "group_file": "tests/demo_inventory/groups.yaml",
        },
    },
)

# Test my stuff
raw_cmd_output = "Interface              IP-Address      OK? Method Status                Protocol\nEthernet0/0            192.168.255.102 YES TFTP   up                    up      \nEthernet0/1            10.1.0.2        YES manual up                    up                          \nEthernet0/2            10.1.0.6        YES manual up                    up      \nEthernet0/3            unassigned      YES unset  administratively down down    \nLoopback0              10.0.0.2        YES manual up                    up      "
dm_cmd_output = {
    "Ethernet0/0": {"ip": "192.168.255.102", "status": "up"},
    "Ethernet0/1": {"ip": "10.1.0.2", "status": "up"},
    "Ethernet0/2": {"ip": "10.1.0.6", "status": "up"},
    "Ethernet0/3": {"ip": "unassigned", "status": "administratively down"},
    "Loopback0": {"ip": "10.0.0.2", "status": "up"},
}
my_list = [1, 2, 3, 4]
my_dict = {
    "dm_cmd_output": dm_cmd_output,
    "my_list": my_list,
    "my_string": "my_string",
    "empty_string": "",
    "none": None,
}


def print_input(task: Task, my_input: str) -> Result:
    return Result(host=task.host, result=my_input)


def return_empty_str(task: Task) -> Result:
    return Result(host=task.host, result="")


def return_none(task: Task) -> Result:
    return Result(host=task.host, result=None)


def without_new_argument_examples(task: Task) -> None:
    task.run(
        name="Example of command output prettified to implement line breaks",
        task=print_input,
        my_input=raw_cmd_output,
    )
    task.run(
        name="Example of a dict input",
        task=print_input,
        my_input=my_dict,
    )
    task.run(
        name="Example of returning an empty string",
        task=return_empty_str,
    )


results = nr.run(task=without_new_argument_examples)
print_result(
    results,
    vars=["name", "result"],
    line_breaks=True,
)


def with_new_argument_examples(task: Task) -> None:
    task.run(
        name="Example of command output prettified to implement line breaks",
        task=print_input,
        my_input=raw_cmd_output,
    )
    task.run(
        name="Example of a dict input",
        task=print_input,
        my_input=my_dict,
    )
    task.run(
        name="Example of returning an empty string",
        task=return_empty_str,
    )


results = nr.run(task=with_new_argument_examples)
print_result(
    results,
    vars=["name", "result"],
    line_breaks=True,
    print_empty_task=False,
    per_panel_var=True,
)
