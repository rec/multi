import threading
import time
import tomlkit
import shlex
import subprocess
import sys
import webbrowser

PROJECT_FILES = 'poetry.lock', 'pyproject.toml'
NONE = object()


def _exit(*args):
    # Elsewhere.
    if args:
        print(*args, file=sys.stderr)
        exit(-1)
    exit(0)


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

    if result is not None:
        _p(project, result)


def assign(project, *argv):
    parts = [(k, v) for k, _, v in a.partition('=') for a in argv]
    if bad := sorted(a for a, (k, v) in zip(argv, parts) if not (k and v)):
        raise ValueError(f'No assignments in {bad}')

    with project.writer() as multi:
        for k, v in parts:
            *rest, last = k.split('.')
            m = multi
            for i in rest:
                m = m.setdefault(i, {})
            m[last] = v


def status(project, *argv):
    if r := project.run_out('git status --porcelain').rstrip():
        _p(project)
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

    if project.is_singleton:
        argv = '-w', project.name + '.py', *argv

    def target():
        mkdocs(project, 'serve', f'--dev-addr={project.server_url}', *argv)

    threading.Thread(target=target, daemon=True).start()

    time.sleep(0.5)
    project.open_server()
    return True


def add_mkdocs(project, *argv):
    pass
