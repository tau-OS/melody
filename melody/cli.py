import click

from melody.output import compile_to_ouput_in_place, write_output_to_directory
from melody.compiler import compile_program_in_place
from melody.dnf import get_dnf_base_from
from melody.program import load_program_tree
from os.path import abspath


@click.group()
@click.version_option("0.1.0")
def cli():
    """An advanced rpm-ostree compose system"""
    pass


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
@click.argument("output", type=click.Path(exists=False))
def compile(filename, output):
    """Compile a melody program to an output directory"""
    node = load_program_tree(abspath(filename), None)
    base = get_dnf_base_from(node)

    compile_program_in_place(node, base)
    write_output_to_directory(node, output, compile_to_ouput_in_place(node))
