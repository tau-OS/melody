import melody.cli
from rich.traceback import install

install(show_locals=True)


def initialise():
    melody.cli.cli()
