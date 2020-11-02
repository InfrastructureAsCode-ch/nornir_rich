import logging
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_rich.functions import print_inventory, print_result, print_failed_hosts

from random import randrange


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
            "host_file": "demo_inventory/hosts.yaml",
            "group_file": "demo_inventory/groups.yaml"
        },
    },
)

def hello_world(task: Task) -> Result:
    return Result(
        host=task.host,
        result=f"{task.host.name} says hello world!"
    )


def say(task: Task, text: str) -> Result:
    return Result(
        host=task.host,
        result=f"{task.host.name} says {text}"
    )

def count(task: Task, number: int) -> Result:
    if randrange(5) == 4:
        raise Exception("Random exception") 
    return Result(
        host=task.host,
        result=f"{[n for n in range(0, number)]}"
    )

def greet_and_count(task: Task, number: int) -> Result:
    task.run(
        name="Greeting is the polite thing to do",
        task=say,
        text="hi!",
    )

    task.run(
        name="Counting beans",
        task=count,
        number=number,
        severity_level=logging.DEBUG
    )
    task.run(
        name="We should say bye too",
        task=say,
        text="bye!",
    )

    # let's inform if we counted even or odd times
    even_or_odds = "even" if number % 2 == 1 else "odd"
    return Result(
        host=task.host,
        result=f"{task.host} counted {even_or_odds} times!"
    )    

results = nr.run(
    task=hello_world
)

print_result(results, expand=True)

results = nr.run(
    task=greet_and_count, number=10
)

print_result(results)
print_result(results, vars=["diff", "result", "name", "exception", "severity_level"])
print_failed_hosts(results)

print_inventory(nr)