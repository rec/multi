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


def bump_version(p, rule_or_version='minor'):
    if not p.version:
        return
    if p.git.is_dirty():
        p.p('Dirty!')
        return
    msg = p.git('l', '-1', '--format=%s', out=True).strip()
    if msg.startswith('Update version to '):
        return

    print()
    print()

    p.p('bump_version')
    print()
    p.run('rm', '-rf', 'dist/')
    p.p('v' + p.version)
    p.uv('version', '--bump', rule_or_version)
    pv = p.version
    p = p.reload()
    assert pv != p.version, f'{pv=} != {p.version=} failed'
    with p.project_writer() as cfg:
        cfg['tool']['poetry']['version'] = p.version

    version_tag = 'v' + p.version
    p.git.commit(f'Update version to {version_tag}', '-a')
    p.git('tag', version_tag)
    p.git('push', '--tag', '--force-with-lease')
    p.run('gh', 'release', 'create', version_tag, '--generate-notes')

    p.uv('build')
    p.uv('publish')
    return True
