from ..paths import PYPROJECT


def remove(project, *tags):
    removed = False
    for tag in tags:
        try:
            project.tags.remove(tag)
            removed = True
        except ValueError:
            pass

    if removed:
        project.write()
        msg = f'Removed {", ".join(tags)} from multi.tags in {PYPROJECT}'
        project.git.commit(msg, PYPROJECT)
        project.p('Tags:', *project.tags)


def add(project, *tags):
    if tags:
        with project.writer():
            for tag in tags:
                if tag not in project.tags:
                    project.tags.append(tags)
            msg = f'Set multi.tags to {", ".join(tags)} in {PYPROJECT}'
        project.git.commit(msg, PYPROJECT)
        project.p('Tags:', *project.tags)


def fix(project):
    tags = project.multi.pop('multi', None)
    if tags is None:
        return

    if project.name == 'abbrev':
        tags = ['finished']
    else:
        try:
            tags[tags.index('release')] = 'working'
        except ValueError:
            pass

    project.multi['tags'] = tags
    project.write()
    project.git.commit('Fix tags in ' + PYPROJECT, PYPROJECT)
    project.p('Tags:', *project.tags)
