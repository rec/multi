import requests
from . import bump_version
from ..paths import PYPROJECT, POETRY_PROJECT_FILES


def poetry(project, *argv):
    print(project.name + ':')
    project.run.poetry(*argv)
    print()


def update(project):
    assert project.name == 'multi' or not project.git.is_dirty()
    if (project.path / PYPROJECT).exists():
        project.p()
        project.run.poetry('update')
        if project.git.is_dirty():
            project.git.commit('Update dependencies', *POETRY_PROJECT_FILES)


def run_tests(project):
    project.run('/code/dotfiles/bin/run-tests')
