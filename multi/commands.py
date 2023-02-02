import threading
import time
import tomlkit
import shlex
import subprocess
import sys

PROJECT_FILES = 'poetry.lock', 'pyproject.toml'
NONE = object()
EMOJIS = {
    'datacls': '🗂',
    'def_main': '🗣',
    'hardback': '📓',
    'impall': '🛎',
    'loady': '🛍',
    'nmr': '🌐',
    'multi': '📚',
}

DESCS = {
    'blocks':  'Solve a block puzzle',
    'cfgs':  'XDG standard config files',
    'datacls':  'Adds a little to dataclasses',
    'def_main':  'A decorator for main',
    'dek':  'The decorator-decorator',
    'dtyper':  'Call or make dataclasses from `typer` commands',
    'editor':  'Open the default text editor',
    'gitz':  'Tiny useful git commands, some dangerous',
    'hardback':  'Hardcopy backups of digital data',
    'impall':  'Test-import all modules below a given root',
    'loady':  'Load Python code and data from git',
    'multi':  'Manage all my other projects',
    'nmr':  'Name all canonical things',
    'plur':  'Simple universal word pluralizer',
    'runs':  'Run a block of text as a subprocess',
    'safer':  'A safer file opener',
    'sproc':  'Subprocesseses for subhumanses',
    'tdir':  'Create and fill a temporary directory',
    'vl8':  'Perturbed audio',
    'xmod':  'Turn an object into a module',
}


def fix_desc(project):
    desc = project.poetry['description'].strip()

    items = list(enumerate(desc))
    begin = next(i for i, c in items if c.isascii())
    end = next(i for i, c in reversed(items) if c.isascii())

    if begin:
        e1 = desc[:begin].strip()
        e2 = desc[end + 1:].strip()
        desc = desc[begin:end + 1].strip()
    else:
        e1 = e2 = EMOJIS[project.name]

    desc = DESCS.get(project.name, desc)
    desc = f'{e1} {desc} {e2}'
    if project.poetry['description'] == desc:
        return

    _p(project, 'Changed:', desc)
    project.poetry['description'] = desc
    project.write()
    project.run.poetry('lock')
    msg = 'Standardize project description'
    project.git.commit(msg, 'pyproject.toml', *PROJECT_FILES)


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
    _p(project, project.branch())


def run(project, *argv):
    _p(project)
    project.run(*argv)
    print()


def bash(project, *argv):
    _p(project)
    project.run.bash(*argv)
    print()


def single(project, *argv):
    if project.is_singleton:
        print(project.name + ':')


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
