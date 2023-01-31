import threading
import tomlkit
import shlex
import subprocess
import webbrowser

PROJECT_FILES = 'poetry.lock', 'pyproject.toml'
NONE = object()


def _p(project, *args):
    print(f'{project.name:10}: ', *args)


def _getattr(data, a):
    for part in a and a.split('.'):
        try:
            data = data[part]
        except Exception:
            try:
                data = getattr(data, part)
            except AttributeError:
                return
    yield data


def _getattrs(data, argv):
    result = {a: d for a in argv or [''] for d in _getattr(data, a)}

    if len(result) == 1 and len(argv) == 1:
        return result.popitem()[1]
    return result


def prop(project, *argv):
    _p(project, _getattrs(project, argv))


def call(project, func, *args):
    try:
        f = _getattrs(project, [func])
        result = f(*args)
    except Exception as e:
        result = e

    _p(project, result)


def status(project, *argv):
    if r := project.run_out('git status --porcelain').rstrip():
        _(project)
        print(r)


def branch(project, *argv):
    _print(project, project.branch())


def run(project, *argv):
    _print(project)
    project.run(*argv)
    print()


def bash(project, *argv):
    _print(project)
    project.run.bash(*argv)
    print()


def single(project, *argv):
    if project.is_singleton:
        print(project.name + ':')


def web(project, *argv):
    url = '/'.join((f'https://github.com/rec/{project.name}', *argv))
    webbrowser.open(url, 1)


def run_poetry(project, *argv):
    print(project.name + ':')
    project.poetry(*argv)
    print()


def mkdocs(project, *argv):
    from . import multi

    path = str(multi.MULTI.bin_path / 'mkdocs')
    project.run(path, *argv)


def serve(project, *argv):
    finished = None

    def target():
        import time

        time.sleep(0.5)
        webbrowser.open('http://127.0.0.1:8000/', 2)

    threading.Thread(target=target).start()

    if project.is_singleton:
        argv = '-w', project.name + '.py', *argv

    mkdocs(project, 'serve', *argv)


def add_mkdocs(project, *argv):
    pass
