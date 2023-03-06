from .. paths import PYPROJECT


def bump_version(project, rule_or_version):
    project.run.poetry('version', rule_or_version)
    project.reload()

    version = 'v' + project.poetry['version']
    project.git.commit(f'Update to version {version}', PYPROJECT)
    project.git('tag', version)
    project.git('push', '--tag', '--force-with-lease')
    project.run('gh', 'release', 'create', version, '--generate-notes')
    project.run.poetry('publish', '--build')


def poetry(project, *argv):
    print(project.name + ':')
    project.run.poetry(*argv)
    print()
