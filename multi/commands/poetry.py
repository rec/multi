def poetry(project, *argv):
    print(project.name + ':')
    project.run.poetry(*argv)
    print()
