from multi.commands import get
from multi.paths import PYPROJECT


prop = get.get_or_call


def exists(project, *args):
    return project.make_path(*args).exists()


def has_emoji(project):
    return not project.description.isascii()


def needs_release(project):
    return project.git_tag != 'v' + project.version


def is_rst(project):
    return project.manager['readme'].endswith('.rst')


def tag(project, *tags):
    return set(project.tags) & set(tags)


def has_old_data(project):
    return 'multi' in project.configs['tool']


def has_test_deps(project):
    try:
        deps = set(project.manager['dependencies'])
    except KeyError:
        return False
    return deps.intersection(('pytest', 'tdir', 'ruff', 'mypy', 'isort', 'black'))


def bad_sync(project):
    try:
        if project.manager:
            project.run.in_venv('uv', 'sync', out=True, no_error=True)
    except Exception as e:
        return True
