from .. projects import GITHUB_IO, MULTI
from . bump_version import bump_version
from ..paths import PROJECT_FILES


FAVICON = GITHUB_IO.path / 'docs/favicon.ico'
assert FAVICON.exists()

SIZE = 72
PREFIX = 'https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2'


def add_coverage(project):
    if not project.pyproject_file.exists():
        return

    has_coverage = 'coverage = ' in project.pyproject_file.read_text()
    if has_coverage:
        return

    if project.name not in ('threa', 'fil', 'gitz', 'litoid', 'plur'):
        return
    project.p('adding')

    if True:
        return

    project.run('poetry', 'add', 'coverage')
    project.git.commit('Add coverage dependency', *PROJECT_FILES)


def get_url(text):
    n = ord(text[0])
    return f'{PREFIX}/{SIZE}x{SIZE}/{n:x}.png'


def favicon(project):
    favicon = project.gh_pages / 'assets/images/favicon.png'
    if not favicon.exists():
        return
    url = get_url(project.description)

    project.run('curl', url, '-o', favicon)
    msg = 'Rewrite favicon from emoji'
    project.git.commit(msg, favicon, cwd=project.gh_pages)


def refurb(project):
    src = project.name + project.is_singleton * '.py'
    r = MULTI.run('refurb', project.path / src, complete=True)
    result = r.stdout + r.stderr
    if lines := list(_fix_lines(result.splitlines())):
        project.p('Errors', *lines, sep='\n')
        print()


def _fix_lines(lines):
    for line in lines:
        if all(c in line for c in '[]'):
            file_location, line = line.split('[', maxsplit=1)
            _, line = line.split(']', maxsplit=1)
            yield file_location.strip() + line


def _glob(project, *globs):
    return sorted(f for g in globs for f in project.path.glob(g))


def cat(project, *globs):
    for f in _glob(project, *globs):
        print(f'\n{f}:\n{f.read_text().rstrip()}')


def glob(project, *globs):
    project.p(*_glob(project, *globs))


_GREP = 'grep --exclude-dir={build,htmlcov} -nHIR * --include \\*.py -e'


def grep(project):
    project.p()
    try:
        project.run(*_GREP.split(), '__version__')
    except Exception:
        print('---')
        raise


def update_python(project):
    if not {'production-ready', 'beta'}.intersection(project.tags):
        return

    try:
        dependencies = project.poetry['dependencies']
        if not dependencies['python'].endswith('3.7'):
            return
    except KeyError:
        return

    project.p('Updating', project.poetry['version'])
    if not True:
        return
    dependencies['python'] = '>=3.8'
    project.write_pyproject()
    project.run('poetry', 'lock', arm=True)

    project.git.commit('Update minimum Python version to 3.8', *PROJECT_FILES)
    bump_version(project, 'minor')
    project.p('Done', project.poetry['version'])


def bad_versions(project):
    import re
    search = re.compile(r'\bv\d+\.\d+\.\d+$').search

    poetry_version = project.poetry.get('version', None)
    for commit in project.git.commits('-10'):
        h, cd, s = commit.split('|')
        if m := search(s):
            git_version = m.group()[1:]
            if poetry_version == git_version:
                return
            else:
                break
    else:
        return

    project.p(poetry_version, git_version)
    bump_version(project, 'patch')
