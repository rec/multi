import safer


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
    readme = project.path / 'README.md'
    url = f'https://rec.github.io/{project.name}'
    anchor = project.api_anchor
    link = f'\n\n### [API Documentation]({url}#{anchor})\n'

    with safer.open(readme, 'w') as fp:
        fp.write(project.comment)
        fp.write(link)

    project.poetry['readme'] = 'README.me'
    project.write_pyproject()
    msg = 'Rename README.rst to README.md'
    project.git.commit(msg, 'README.rst', 'README.md', 'pyproject.toml')
    project.open_git()


def readme(project):
    project.p((project.path / 'README.md').open().readline())
    project.write_pyproject()
