from platform import machine
from os.path import dirname
import dnf
from anytree import Node

from melody.program import query_releasever, query_required_repos

import dnf
from rich.progress import Progress, SpinnerColumn, DownloadColumn, TransferSpeedColumn
from rich.console import Console

console = Console()

# Shamefully stolen from layering-package-manager
class ProgressMetre(dnf.callback.DownloadProgress):
    """Multi-file download progess metre"""

    progress_bar = Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        DownloadColumn(),
        TransferSpeedColumn(),
    )

    def __init__(self):
        self.total_files = 0
        self.total_size = 0
        self.total_drpm = 0
        self.tasks = {}
        self.download_size = {}

        self.done_size = 0
        self.done_files = 0

    def start(self, total_files, total_size, total_drpms=0):
        self.total_files = total_files
        self.total_size = total_size
        self.total_drpm = total_drpms
        self.tasks = {}
        self.download_size = {}

        self.progress_bar.__enter__()
        self.progress_bar.start()

    def progress(self, payload, done):
        name = payload.__str__()
        if payload.download_size != 0:
            self.download_size[name] = payload.download_size

        payload_size = self.download_size.get(name, 0)

        if not name in self.tasks:
            self.tasks[name] = self.progress_bar.add_task(name, total=payload_size)

        self.progress_bar.update(self.tasks[name], completed=done, total=payload_size)

    def end(self, payload, status, err_msg):
        payload_size = self.download_size.get(payload.__str__(), 0)

        if self.progress_bar.finished == True:
            self.progress_bar.stop()
            self.progress_bar.__exit__(None, None, None)

        if err_msg:
            console.print(f"{err_msg}")

        self.progress_bar.update(
            self.tasks[payload.__str__()],
            completed=payload_size,
            total=payload_size,
        )


def get_dnf_base_from(program: Node) -> dnf.Base:
    base = dnf.Base()
    conf = base.conf

    conf.reposdir = [dirname(program.file_path)]

    conf.substitutions["releasever"] = query_releasever(program)
    conf.substitutions["basearch"] = machine()

    base.read_all_repos()
    base.repos.all().disable()
    for repo in query_required_repos(program):
        repo_obj = base.repos.get(repo)
        repo_obj.enable()
        repo_obj.set_progress_bar(ProgressMetre())

    base.fill_sack(load_system_repo=False, load_available_repos=True)
    base.read_comps(arch_filter=True)

    return base


def get_packages_for_group(group: str, base: dnf.Base) -> list:
    return [p.name for p in base.comps.group_by_pattern(group).packages_iter()]
