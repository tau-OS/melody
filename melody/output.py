from anytree import Node, PreOrderIter
from os.path import dirname, join, normpath
from melody.program import listify
from pathlib import Path
import yaml
from glob import glob
import shutil


def find_child_by_path(node, path):
    for child in node.children:
        if child.file_path == path:
            return child
    return None


def compile_to_ouput_in_place(program: Node) -> list[(int, str)]:
    """Compile a program to a standard rpm-ostree treefile in place"""
    index = 0
    for node in PreOrderIter(program):
        node.index = index
        index += 1

    files_to_copy = []

    for node in PreOrderIter(program):
        if "arch-include" in node.data:
            for arch in listify(node.data["arch-include"]):
                node.data["arch-include"][arch] = list(
                    map(
                        lambda include: str(
                            find_child_by_path(
                                node, normpath(join(dirname(node.file_path), include))
                            ).index
                        )
                        + ".yaml",
                        listify(node.data["arch-include"][arch]),
                    )
                )

        if "conditional-include" in node.data:
            for condition in node.data["conditional-include"]:
                condition["include"] = list(
                    map(
                        lambda include: str(
                            find_child_by_path(
                                node, normpath(join(dirname(node.file_path), include))
                            ).index
                        )
                        + ".yaml",
                        listify(condition["include"]),
                    )
                )

        if "include" in node.data:
            node.data["include"] = list(
                map(
                    lambda include: str(
                        find_child_by_path(
                            node, normpath(join(dirname(node.file_path), include))
                        ).index
                    )
                    + ".yaml",
                    listify(node.data["include"]),
                )
            )

        if "check-passwd" in node.data:
            print("owo")
            files_to_copy.append(
                (
                    index,
                    normpath(
                        join(
                            dirname(node.file_path),
                            node.data["check-passwd"]["filename"],
                        )
                    ),
                )
            )
            node.data["check-passwd"]["filename"] = str(index) + ".yaml"
            index += 1

        if "check-group" in node.data:
            files_to_copy.append(
                (
                    index,
                    normpath(
                        join(
                            dirname(node.file_path),
                            node.data["check-group"]["filename"],
                        )
                    ),
                )
            )
            node.data["check-group"]["filename"] = str(index) + ".yaml"
            index += 1

        print(files_to_copy)
        return files_to_copy


def write_output_to_directory(
    program: Node, directory: str, files_to_copy: list[(int, str)]
):
    Path(directory).mkdir(parents=True, exist_ok=True)

    for node in PreOrderIter(program):
        with open(join(directory, str(node.index) + ".yaml"), "w") as f:
            yaml.dump(node.data, f)

    base_dir = dirname(program.file_path)
    for repo in glob("*.repo", root_dir=base_dir):
        shutil.copy(join(base_dir, repo), directory)

    for (index, filename) in files_to_copy:
        shutil.copy(filename, join(directory, str(index) + ".yaml"))
