from pathlib import Path

from . import projects

MKDOCS = Path(__file__).parents[1] / 'mkdocs'
MKDOCS_BINARY = str(projects.MULTI.bin_path / 'mkdocs')
PYPROJECT = 'pyproject.toml'
