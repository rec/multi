from . import projects
from pathlib import Path

MKDOCS = Path(__file__).parents[1] / 'mkdocs'
MKDOCS_BINARY = str(projects.MULTI.bin_path / 'mkdocs')
PYPROJECT = 'pyproject.toml'
PROJECT_FILES = 'poetry.lock', PYPROJECT
