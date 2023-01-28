#!/usr/bin/env python3

from pathlib import Path
import json
from typer import Option, Typer

__all__ = 'app', 'command'

PROJECTS_FILE = Path(__file__).parent / 'projects.json'
PROJECTS = json.loads(PROJECTS_FILE.read_text())

app = Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    help=f'')

command = app.command


@command(name='list')
def _list():
    print(*sorted(PROJECTS), sep='\n')


if __name__ == '__main__':
    app(standalone_mode=False)
