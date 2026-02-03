from ..paths import PYPROJECT


def print_gh(p):
    p.p()
    try:
        p.run('gh', 'repo', 'set-default', '--view', out=True)
    except Exception:
        p.p('FAIL')
    except:
        p.p("FUCK!")


def name_dirname(p):
    if p.manager and p.name != p.manager["name"]:
        p.p(p.name, p.manager["name"])


def bump_version(project, rule_or_version='minor'):
    if not (pv := project.version):
        return
    msg = project.git('l', '-1', '--format=%s', out=True).strip()
    if msg.startswith('Update version to '):
        return
    if project.git.is_dirty():
        project.p('Dirty!')
        return
    if not True:
        project.p()
        return
    print()
    print()
    project.p('bump_version')
    print()
    project.run('rm', '-rf', 'dist/')
    project.p('v' + pv)
    project.uv('version', '--bump', rule_or_version)
    project = project.reload()
    assert pv != project.version, pv

    version = 'v' + project.version
    project.git.commit(f'Update version to {version}', '-a')
    project.git('tag', version)
    project.git('push', '--tag', '--force-with-lease')
    project.run('gh', 'release', 'create', version, '--generate-notes')

    project.uv('build')
    project.uv('publish')
