from multi.commands.get import get_or_call


def exists(project, *args):
    return project.joinpath(*args).exists()


def has_emoji(project):
    return not project.description.isascii()


def needs_release(project):
    return project.git_tag != 'v' + project.poetry['version']


def is_rst(project):
    return project.poetry['readme'].endswith('.rst')


def tag(project, *tags):
    return set(project.tags) & set(tags)


def has_old_data(project):
    return 'multi' in project.configs['tool']


def has_test_deps(project):
    try:
        deps = set(project.configs['tool']['poetry']['dependencies'])
    except KeyError:
        return False
    return deps.intersection(('pytest', 'tdir', 'ruff', 'mypy', 'isort', 'black'))


prop = get_or_call
has_tags = tag  # legacy
