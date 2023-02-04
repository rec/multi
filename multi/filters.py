def is_dirty(project):
    return project.git.is_dirty


def is_singleton(project):
    return project.is_singleton


def has_emoji(project):
    return not project.poetry['description'].isascii()


def needs_release(project):
    return project.git_tag != 'v' + project.poetry['version']


def is_rst(project):
    return project.poetry['readme'].endswith('.rst')


def is_md(project):
    return project.poetry['readme'].endswith('.md')


def has_tags(project, *tags):
    return set(project.tags) & set(tags)
