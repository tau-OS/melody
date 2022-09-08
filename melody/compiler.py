import copy
import itertools
from anytree import Node, PreOrderIter
from melody.dnf import get_packages_for_group
import dnf


def compile_in_place(data: dict[str, any], base: dnf.Base):
    """Compile to a standard rpm-ostree treefile in place"""
    if "groups" in data:
        groups = data["groups"]
        if "groups" in data:
            del data["groups"]

        packages = list(
            itertools.chain.from_iterable(
                map(
                    lambda g: filter(
                        lambda p: p in (g.get("blacklist", [])),
                        get_packages_for_group(g["id"], base),
                    ),
                    groups,
                )
            )
        )

        if "packages" not in data:
            data["packages"] = []

        data["packages"].extend(packages)


def compile_program_in_place(program: Node, base: dnf.Base):
    """Compile a program to a standard rpm-ostree treefile in place"""
    for node in PreOrderIter(program):
        compile_in_place(node.data, base)
