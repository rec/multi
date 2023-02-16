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
        project.write_pyproject()
        msg = f'Removed {", ".join(tags)} from multi.tags in {PYPROJECT}'
        project.git.commit(msg, PYPROJECT)
        project.p('Tags:', *project.tags)


def add(project, *tags):
    if adds := [t for t in tags if t not in project.tags]:
        with project.writer():
            project.tags.extend(adds)
            msg = f'Add {", ".join(adds)} to multi.tags in {PYPROJECT}'

            project.git.commit(msg, PYPROJECT)
            project.p('Added tags:', *adds)


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
    project.write_pyproject()
    project.git.commit('Fix tags in ' + PYPROJECT, PYPROJECT)
    project.p('Tags:', *project.tags)
