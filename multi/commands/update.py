from contextlib import suppress
import re
import safer

MSG = 'use "git push" to publish your local commits'


def push_unpushed(project):
     if MSG in project.git('status', out=True):
         project.git('push')


def fix_single_file(project):
    project.configs['build-system'] = {
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
    if not (v := p.partition(",")[0].partition('3.')[2].partition(".")[0]):
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
        project.configs['project']['requires-python'] = ">=3.10"
        project.write_pyproject()
        project.run.in_venv('uv', 'sync')
        project.git.comp('Update python version to 3.10', '-a')

    elif project.git.is_dirty():
        project.git.comp('Fix .python-version', '-a')


def upgrade(project):
    project.run.in_venv('uv', 'sync', '--upgrade')
    if project.git.is_dirty():
        project.git.comp('Upgrade dependencies', 'uv.lock')


def migrate_to_uv(project):
    if project.package_manager != 'poetry':
        return

    project.p('*** UPDATE ***')
    project.run('uvx', 'migrate-to-uv', '--package-manager', 'poetry')
    project.run('uv', 'venv')
    project.run.in_venv('uv', 'sync')
    project.run('uv', 'lock')
    with suppress(FileNotFoundError):
        project.make_path(".envrc").unlink()

    if (p := project.make_path(".direnv")).exists():
        p.rename(p.parent / 'old.direnv')

    project.git('add', 'uv.lock')
    project.git('commit', '-am', 'Migrate from poetry to uv')
