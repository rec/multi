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

    print(f'{project.name:10}:', res)


def poetry(project, *argv):
    data = project.poetry_data

    def get_address(a):
        d = data
        for part in a and a.split('.'):
            try:
                d = d[part]
            except TypeError:
                try:
                    d = getattr(d, part)
                except AttributeError:
                     return
        yield d

    result = {a: v for a in argv or [''] for v in get_address(a)}
    if len(result) == 1 and len(argv) <= 1:
        _, result = result.popitem()

    print(f'{project.name:10}:', result)


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


def run_poetry(project, *argv):
    print(project.name + ':')
    project.poetry(*argv)
    print()


def add_mkdocs(project, *argv):
    pass
