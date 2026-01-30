from contextlib import suppress


def update(project):
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
