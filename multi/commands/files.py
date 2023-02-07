def clean_dir(project):
    print(f'cd {project.path}')
    print('direnv reload')
    print('poetry --no-ansi install')


def _glob(project, *globs):
    return sorted(f for g in globs for f in project.path.glob(g))


def cat(project, *globs):
    for f in _glob(project, *globs):
        print(f'\n{f}:\n{f.read_text().rstrip()}')


def glob(project, *globs):
    project.p(*_glob(project, *globs))


def add_sponsor(project):
    sf = project.path / 'FUNDING.yml':
    if not sf.exists():
        sf.write_text('github: rec\n')
        project.git.commit('Added FUNDING.yml', sf)
