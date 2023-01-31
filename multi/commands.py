from functools import partial
import tomlkit
import shlex
import subprocess
import webbrowser

PROJECT_FILES = 'poetry.lock', 'pyproject.toml'


def prop(project, *argv):
    res = {k: getattr(project, k) for k in argv}
    if len(res) == 1:
        res = res.popitem()[1]

    print(f'{project.name:12}:', res)


def status(project, *argv):
    if r := project.run_out('git status --porcelain').rstrip():
        print(project.name + ':')
        print(r)


def branch(project, *argv):
    print(f'{project.name:12}: {project.branch()}')


def run(project, *argv):
    print(project.name + ':')
    project.run(*argv)
    print()


def run_in(project, *argv):
    print(project.name + ':')
    project.run_in(*argv)
    print()


def single(project, *argv):
    if project.is_singleton:
        print(project.name + ':')


def web(project, *argv):
    url = '/'.join((f'https://github.com/rec/{project.name}', *argv))
    webbrowser.open(url, 1)


def bash(project, *argv):
    print(project.name + ':')
    project.run('bash', '-c', shlex.join(argv))
    print()


def poetry(project, *argv):
    print(project.name + ':')
    project.poetry(*argv)
    print()


def add_mkdocs(project, *argv):
    pass
