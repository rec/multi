from .. import configs
import safer


def filename(project):
    return project.path / 'README.md'


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
    project.p()
    fname = filename(project)
    contents = fname.read_text()

    _write_readme(project)

    if configs.push and contents != fname.read_text():
        project.git.commit(f'Update README.md from {project.name}.py', fname)
