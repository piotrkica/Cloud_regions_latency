from typing import Callable
from azure.core.polling import LROPoller


def cleanup_resource_sequential(names: "list[str]", delete_funcs: "list[Callable[[], LROPoller[None]]]"):
    # Some requests failed during concurrent deleting
    for (name, delete_func) in zip(names, delete_funcs):
        try:
            result = delete_func()
            result.result()
            print(f"Deleted {name}")
        except:
            print(f"Failure during cleaning resource {name}")


def cleanup_resource(names: "list[str]", delete_funcs: "list[Callable[[], LROPoller[None]]]"):
    delete_results = []
    for (name, delete_func) in zip(names, delete_funcs):
        try:
            delete_results.append((name, delete_func()))
        except:
            print(f"Failure during cleaning resource {name}")

    for (name, delete_result) in delete_results:
        delete_result.result()
        print(f"Deleted {name}")
