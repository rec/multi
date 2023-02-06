from ..paths import PYPROJECT


def remove_tag(project, *tags):
    removed = False
    for tag in tags:
        try:
            project.tags.remove(tag)
            removed = True
        except ValueError:
            pass

    if removed:
        if not project.tags:
            del project.poetry['tags']
        project.write()
        project.p('Tags:', *project.tags)


def add_tag(project, *tags):
    if tags:
        with project.writer():
            project.tags.extend(tags)
            msg = f'Set multi.tags to {", ".join(tags)} in {PYPROJECT}'
        project.git.commit(msg, PYPROJECT)
        project.p('Tags:', *project.tags)
