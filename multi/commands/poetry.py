import requests
from . import bump_version
from ..paths import PYPROJECT, PROJECT_FILES


def poetry(project, *argv):
    print(project.name + ':')
    project.run.poetry(*argv)
    print()


def add_fields(project):
    tool = project.configs.setdefault('tool', {}).setdefault('poetry', {})
    old_tool = dict(tool)

    tool['repository'] = project.git_url
    tool['homepage'] = project.git_url

    if _exists(project.doc_url):
        tool['documentation'] = project.doc_url

    if False or tool != old_tool:
        project.commit_pyproject('Add fields to [tool.poetry] in pyproject.toml')
        bump_version.bump_version(project, 'patch')
        project.p('Done')
    else:
        project.p(tool)


def update(project):
    assert project.name == 'multi' or not project.git.is_dirty()
    if (project.path / PYPROJECT).exists():
        project.p()
        if not False:
            project.run.poetry('update')
            if project.git.is_dirty():
                project.git.commit('Update dependencies', *PROJECT_FILES)


def remove_cruft(project):
    tools = 'black', 'flake8', 'isort'
    removed = [k for k in tools if project.configs['tool'].pop(k, None)]
    if any(removed):
        project.write_pyproject()
        project.git.commit('Removed tool configs for ' + ', '.join(removed), PYPROJECT)


def add_strict(project):
    mypy = project.configs['tool'].setdefault('mypy', {})
    if not mypy.get('strict'):
        mypy['strict'] = True
        project.write_pyproject()
        project.git.commit('Run mypy in strict mode', PYPROJECT)


def _exists(url):
    try:
        value = requests.get(url)
    except Exception:
        return False
    else:
        return value.status_code == 200
