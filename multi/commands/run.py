def run(project, *argv):
    project.p()
    project.run(*argv)
    print()


def bash(project, *argv):
    project.p()
    project.run.bash(*argv)
    print()
