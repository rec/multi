from contextlib import suppress
from subprocess import CalledProcessError
import re
import safer

MSG = 'use "git push" to publish your local commits'

_COVERAGE_REPORT_DEFAULT = {
    'skip_covered': True,
    'exclude_lines': [
        'pragma: no cover',
        'if False:',
        'if __name__ == .__main__.:',
        'raise NotImplementedError',
    ],
}


def fix_quote_style(p):
    if not p.cfg or p.name == 'test':
        return

    format = p.sub_cfg('tool', 'ruff', 'format')
    if format.get('quote-style') == 'single':
        return

    p.p('fix_quote_style')
    format['quote-style'] = 'single'
    p.write_pyproject()
    p.run.in_venv('ruff', 'format')
    p.git.comp('Return to using single quotes', '-a')


def classify(project):
    minor = int(project.python_version.split('.')[1])
    nums = ('3', *(f'3.{i}' for i in range(minor, 15)))
    classifiers = [f'Programming Language :: Python :: {n}' for n in nums]
    project.cfg['project']['classifiers'] = classifiers
    project.write_pyproject()
    if project.git.is_dirty():
        project.p('classify!')
        project.git(
            'commit',
            '-m',
            'Fix tools.classifiers section in pyproject.toml',
            'pyproject.toml',
        )
        project.git('push', '--force-with-lease')


def mypy_tool(project):
    try:
        project.cfg['tool'].pop('mypy')
    except KeyError:
        pass
    else:
        project.write_pyproject()
        project.git(
            'commit', '-m', 'Remove tool.mypy from pyproject.toml', 'pyproject.toml'
        )
        project.git('push', '--force-with-lease')


def duplicate_commits(project):
    s = project.git('l', '-2', '--format=%s', out=True).splitlines()
    if s[0] == s[1]:
        project.p()
        project.git('permute', 'ab', '-s')
        project.git('push', '-f')


def uniform_toolchain(project):
    added = 'coverage pyupgrade ruff ty'.split()
    removed = 'black doks flake8 isort mypy'.split()

    cfg = project.cfg
    dev = cfg.get('dependency-groups', {}).get('dev', [])
    dev = {i.partition('>')[0].partition('^')[0] for i in dev}

    if set(added) <= dev and not (set(removed) & dev):
        return

    coverage = cfg.setdefault('tool', {}).setdefault('coverage', {})
    coverage.setdefault('run', {})['branch'] = True
    coverage.setdefault('report', {}).update(_COVERAGE_REPORT_DEFAULT)
    project.write_pyproject()

    project.run.in_venv(*('uv add --dev coverage pyupgrade ruff ty'.split()))
    for remove in removed:
        if remove in dev:
            project.run.in_venv(*(f'uv remove --dev {remove}'.split()))
    msg = 'Make dev dependencies uniform between projects'
    project.git.comp(msg, 'pyproject.toml', 'uv.lock')


def push_unpushed(project):
    if MSG in project.git('status', out=True):
        project.git('push')


def fix_single_file(project):
    project.cfg['build-system'] = {
        'requires': ['hatchling'],
        'build-backend': 'hatchling.build',
    }
    project.write_pyproject()
    project.git.comp('Fix uv sync', 'pyproject.toml')


def old_fix_single_file(project):
    single_file = project.path / (project.name + '.py')
    if single_file.exists():
        project.p()
        if not True:
            return
        (project.path / project.name).mkdir()

        src, target = str(single_file), f'{project.name}/__init__.py'
        project.git('mv', src, target)
        project.git.comp(f'Rename {src} to {target}')


def update_to_310(project):
    p = project.python_version
    if not (v := p.partition(',')[0].partition('3.')[2].partition('.')[0]):
        return
    project.p('update')
    version = int(v)

    ignore_path = project.path / '.gitignore'
    text = ignore_path.read_text()
    with safer.open(ignore_path, 'w') as fp:
        state = 0
        for line in text.splitlines(keepends=True):
            if line.startswith('# pyenv'):
                state = 1
            elif state == 1:
                if '.python-version' in line:
                    state = 2
            elif state == 2:
                if line.strip():
                    fp.write(line)
                state = 0
            elif '.python-version' not in line:
                assert state == 0, (state, line, prev)
                fp.write(line)
            prev = line

    f = project.path / '.python-version'
    text = f'3.{max(version, 10)}\n'
    if not f.exists() or f.read_text() != text:
        f.write_text(text)
    project.git('add', str(f))

    if version < 10:
        project.cfg['project']['requires-python'] = '>=3.10'
        project.write_pyproject()
        project.run.in_venv('uv', 'sync')
        project.git.comp('Update python version to 3.10', '-a')

    elif project.git.is_dirty():
        project.git.comp('Fix .python-version', '-a')


def upgrade(project):
    project.run.in_venv('uv', 'sync', '--upgrade')
    if project.git.is_dirty():
        project.git.comp('Upgrade dependencies', 'uv.lock')
