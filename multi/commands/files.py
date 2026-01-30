import configparser
import shutil
from .. projects import GITHUB_IO, MULTI
from . bump_version import bump_version
from ..paths import POETRY_PROJECT_FILES, PYPROJECT


FAVICON = GITHUB_IO.path / 'docs/favicon.ico'
assert FAVICON.exists()

SIZE = 72
PREFIX = 'https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2'


def fix_coveragerc(project):
    try:
        exclude_lines = project.configs['tool']['coverage']['report']['exclude_lines']
    except KeyError:
        return
    if not exclude_lines[0]:
        while exclude_lines and not exclude_lines[0]:
            exclude_lines.pop(0)

    project.commit_pyproject(f'Move .coveragerc into {PYPROJECT}')


def fix_coveragerc2(project):
    first, second = (i.split('|')[-1] for i in project.git.commits('-2'))
    if first != second:
        return

    project.git('commit', '--amend', '-m',
                'Remove empty line in pyproject coverage section')
    project.git('push', '--force-with-lease')


def move_coveragerc(project):
    cov = project.path / '.coveragerc'
    if not cov.exists():
        return

    config = configparser.ConfigParser()
    config.read(cov)
    c = {k: dict(config[k]) for k in config.sections()}

    if exclude_lines := c.get('report', {}).get('exclude_lines'):
        c['report']['exclude_lines'] = exclude_lines.split('\n')

    project.configs['tool']['coverage'] = c

    if True:
        project.p()
        return

    project.write_pyproject()
    cov.unlink()
    project.git.commit(f'Move .coveragerc into {PYPROJECT}', PYPROJECT, cov)



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
        dependencies = project.manager['dependencies']
        if not dependencies['python'].endswith('3.7'):
            return
    except KeyError:
        return

    project.p('Updating', project.version)
    if not True:
        return
    dependencies['python'] = '>=3.8'
    project.write_pyproject()
    project.run('poetry', 'lock', arm=True)

    project.git.commit('Update minimum Python version to 3.8', *POETRY_PROJECT_FILES)
    bump_version(project, 'minor')
    project.p('Done', project.version)


def remove_workflows(project):
    if not (project.path / '.github').exists():
        return
    package = project.path / '.github/workflows/python-package.yml'
    if package.exists():
        project.git('rm', str(package))
        project.git('commit', '-m', 'Stop running github workflows')
