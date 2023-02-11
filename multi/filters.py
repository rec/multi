from multi.commands.get import get_or_call


def exists(project, *args):
    return project.joinpath(*args).exists()


def has_emoji(project):
    return not project.poetry['description'].isascii()


def needs_release(project):
    return project.git_tag != 'v' + project.poetry['version']


def is_rst(project):
    return project.poetry['readme'].endswith('.rst')


def tag(project, *tags):
    return set(project.tags) & set(tags)


prop = get_or_call
has_tags = tag  # legacy
