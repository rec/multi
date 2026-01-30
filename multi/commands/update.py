from contextlib import suppress
import re

MSG = 'use "git push" to publish your local commits'


def push_unpushed(project):
     if MSG in project.git('status', out=True):
         project.git('push')


def fix_single_file(project):
    single_file = project.path / (project.name + '.py')
    if single_file.exists():
        project.p()
        if not True:
            return
        (project.path / project.name).mkdir()

        src, target = str(single_file), f'{project.name}/__init__.py'
        project.git('mv', src, target)
        project.git.comp(f'Rename {src} to {target}')


update = fix_single_file


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
