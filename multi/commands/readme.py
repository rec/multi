import safer


def filename(project):
    return project.path / 'README.md'


def fix_readme(project):
    project.p(project.poetry['readme'])
    if project.poetry['readme'].endswith('.me'):
        project.poetry['readme'] = 'README.md'
        project.write_pyproject()
        project.git.commit('Fix typo in pyproject.toml', 'pyproject.toml')


def rename_readme(project):
    if not project.poetry['readme'].endswith('.rst'):
        return

    project.git('mv', 'README.rst', 'README.md')

    _write_readme(project)

    project.poetry['readme'] = 'README.md'
    project.write_pyproject()
    msg = 'Rename README.rst to README.md'
    project.git.commit(msg, 'README.rst', 'README.md', 'pyproject.toml')
    project.open_git()


def readme(project):
    project.p(filename(project).open().readline())
    project.write_pyproject()


def _write_readme(project):
    url = f'https://rec.github.io/{project.name}'
    anchor = project.api_anchor
    link = f'\n\n### [API Documentation]({url}#{anchor})\n'

    with safer.open(filename(project), 'w') as fp:
        fp.write(project.comment)
        fp.write(link)


def write_readme(project):
    fname = filename(project)
    contents = fname.read_text()

    _write_readme(project)

    if contents != fname.read_text():
        project.git.commit(f'Update README.py from {project.name}.py', fname)


def fix_mistake(project):
    line = project.git('l', '-1', out=True)
    if 'README.py' not in line:
        return
    project.git('commit', '--amend', '-m', 'Update README.md from dtyper.py')
    project.git('push', '--force-with-lease')


def fix_stupid_mistake(project):
    if project.name == 'dtyper':
        return
    line = project.git('l', '-1', out=True)
    if 'dtyper' not in line:
        return
    msg = f'Update README.md from {project.name}.py'
    project.p()
    # project.p(line, msg, sep='\n')
    if not True:
        return
    project.git('commit', '--amend', '-m', msg)
    project.git('push', '--force-with-lease')
