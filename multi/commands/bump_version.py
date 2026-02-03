from ..paths import PYPROJECT


def bump_version(project, rule_or_version='minor'):
    if project.git.is_dirty():
        project.p('Dirty!')
        return
    if not (pv := project.version):
        return
    project.run('rm', '-rf', 'dist/')
    project.p('v' + pv)
    project.uv('version', '--bump', rule_or_version)
    project = project.reload()
    assert pv != project.version, pv

    version = 'v' + project.version

    project.git.commit(f'Update version to {version}', '-a')
    if not True:
        return
    project.git('tag', version)
    project.git('push', '--tag', '--force-with-lease')
    project.run('gh', 'release', 'create', version, '--generate-notes')

    project.uv('build')
    project.uv('publish')
