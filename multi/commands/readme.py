from ..paths import PROJECT_FILES


def open_readme(project):
    if project.branch() == 'rst-to-md':
        print(project.name + ':')
        project.open_git()
        project.open_git('tree/rst-to-md')


def readme(project):
    if files := sorted(project.path.glob('README.*')):
        project.run('wc', '-l', *files)


def rename_readme(project):
    src = project.poetry['readme']
    if not src.endswith('.rst'):
        return

    print(project.name + ':\n')
    root = src.removesuffix('.rst')
    target = root + '.md'
    tmp = root + '-tmp.md'

    branch_name = 'rst-to-md'
    project.git('new', branch_name)
    project.run(f'pandoc {src} -f rst -t markdown -o {tmp}'.split())
    project.git('mv', src, target)
    project.run('mv', tmp, target)
    project.poetry['readme'] = target
    project.write_pyproject()
    project.run.poetry('lock')

    msg = 'Convert README.rst to README.md'
    project.git.commit(msg, src, target, *PROJECT_FILES)
