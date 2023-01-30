from functools import partial
import tomlkit
import shlex
import subprocess
import webbrowser

PROJECT_FILES = 'poetry.lock', 'pyproject.toml'


def prop(project):
    res = {k: getattr(project, k) for k in project.argv}
    if len(res) == 1:
        res = res.popitem()[1]

    print(f'{project.name:12}:', res)


def status(project):
    if r := project.run_out('git status --porcelain').rstrip():
        print(project.name + ':')
        print(r)


def branch(project):
    print(f'{project.name:12}: {project.branch()}')


def run(project):
    print(project.name + ':')
    project.run(*project.argv)
    print()


def run_in(project):
    print(project.name + ':')
    project.run_in(*project.argv)
    print()


def single(project):
    if project.is_singleton:
        print(project.name + ':')


def web(project):
    url = '/'.join((f'https://github.com/rec/{project.name}', *project.argv))
    webbrowser.open(url, 1)


def bash(project):
    print(project.name + ':')
    project.run('bash', '-c', shlex.join(project.argv))
    print()


def poetry(project):
    print(project.name + ':')
    project.poetry(*project.argv)
    print()


def add_mkdocs(project):
    try:
        print(project.name + ':')
        project.poetry(
            'add', '--dev', 'mkdocs', 'mkdocstrings[python]', 'mkdocs-material'
        )
        project.commit('Add files for mkdirs', *PROJECT_FILES)
        success = True
    finally:
        if not 'success' in locals():
            project.run('git', 'reset', '--hard', 'HEAD')
