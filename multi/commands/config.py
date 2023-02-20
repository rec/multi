from .. import projects


def simplify(project):
    pd = projects.PROJECTS_DATA
    tags = pd.setdefault('tags', {})

    if project.tags:
        for t in sorted(project.tags):
            tags.setdefault(t, []).append(project.name)

        projects.write()
