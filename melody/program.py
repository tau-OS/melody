from typing import Dict, Optional
import yaml
from anytree import Node, PreOrderIter
from os.path import dirname, join, normpath, basename
from platform import machine


def listify(value):
    if isinstance(value, list):
        return value
    return [value]


def parse_value(value: str):
    if value == "true":
        return True
    if value == "false":
        return False

    if (value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'"):
        return value[1:-1]

    return float(value)


def evaulute_condition(condition: str, variables: Dict[str, any]):
    args = condition.split()
    if len(args) != 3:
        raise Exception("Invalid condition")

    if args[0] not in variables:
        raise Exception("Variable not found")

    variable_value = variables[args[0]]
    value = parse_value(args[2])

    if args[1] == "==":
        return value == variable_value
    if args[1] == "!=":
        return value != variable_value
    if args[1] == ">":
        return value > variable_value
    if args[1] == "<":
        return value < variable_value
    if args[1] == ">=":
        return value >= variable_value
    if args[1] == "<=":
        return value <= variable_value

    raise Exception("Invalid condition")


def load_program_tree(
    file_path: str,
    parent: Optional[Node],
    variables: Dict[str, any] = {"basearch": machine()},
):
    with open(file_path, "r") as stream:
        data = yaml.safe_load(stream)
        current = Node(
            basename(file_path), file_path=file_path, parent=parent, data=data
        )

        if "releasever" in data:
            variables["releasever"] = data["releasever"]

        if "variables" in data:
            for key in data["variables"]:
                variables[key] = data["variables"][key]

        include_paths = []

        if "arch-include" in data and machine() in data["arch-include"]:
            for include in listify(data["arch-include"][machine()]):
                include_paths.append(include)

        if "conditional-include" in data:
            for condition in data["conditional-include"]:
                if evaulute_condition(condition["if"], variables):
                    for include in listify(condition["include"]):
                        include_paths.append(include)

        if "include" in data:
            for include in listify(data["include"]):
                include_paths.append(include)

        for include in include_paths:
            include_path = normpath(join(dirname(file_path), include))
            load_program_tree(include_path, current, variables)

        return current


def query_required_repos(program: Node):
    repos = []
    for node in PreOrderIter(program):
        if "repos" in node.data:
            for repo in node.data["repos"]:
                repos.append(repo)

    return repos


def query_releasever(program: Node):
    for node in PreOrderIter(program):
        if "releasever" in node.data:
            return node.data["releasever"]

    return None
