def open_readme(project):
    if project.branch() == 'rst-to-md':
        print(project.name + ':')
        project.open_git()
        project.open_git('tree/rst-to-md')


def readme(project):
    if files := sorted(project.path.glob('README.*')):
        project.run('wc', '-l', *files)
