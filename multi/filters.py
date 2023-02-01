def is_dirty(project):
    return project.git.is_dirty()


def has_emoji(project):
    return not project.poetry['description'].isascii()
