def is_dirty(project):
    return project.git.is_dirty


def has_emoji(project):
    return not project.poetry['description'].isascii()


def needs_release(project):
    return project.git_tag != 'v' + project.poetry['version']


def is_rst(project):
    return project.poetry['readme'].endswith('.rst')
