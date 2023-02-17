def clean_ranks():
    from .. import projects

    rank = [p.name for p in projects.PROJECTS.values()]
    projects.MULTI_DATA['rank'] = rank
    projects.write()


def clean_dir(project):
    print(f'cd {project.path}')
    print('direnv reload')
    print('poetry --no-ansi install')


def _glob(project, *globs):
    return sorted(f for g in globs for f in project.path.glob(g))


def cat(project, *globs):
    for f in _glob(project, *globs):
        print(f'\n{f}:\n{f.read_text().rstrip()}')


def glob(project, *globs):
    project.p(*_glob(project, *globs))


def old_grep(project):
    project.p()
    filename = project.name + '.py'
    re = r'\.\. code-block:: python'
    try:
        project.run('grep', '-e', re, filename)
    except Exception:
        print('---')


_GREP = 'grep --exclude-dir={build,htmlcov} -nHIR * --include \\*.py -e'


def grep(project):
    project.p()
    try:
        project.run(*_GREP.split(), '__version__')
    except Exception:
        print('---')
        raise


def remove_version(project):
    if versions := list(project.path.rglob('VERSION')):
        project.p('Found', *versions)
        v, = versions
        v.unlink()
        project.git.commit(f'Remove {v.relative_to(project.path)}', v)

    if project.is_singleton:
        paths = [project.path / (project.name + '.py')]
    else:
        paths = (project.path / project.name).rglob('*.py')

    for path in paths:
        _remove_version(project, path)


def _remove_version(project, path):
    prefix = '__version__ = '
    lines = path.read_text().splitlines()
    if indexes := [i for i, s in enumerate(lines) if s.startswith(prefix)]:
        line = lines.pop(indexes[0])
        path.write_text('\n'.join(lines) + '\n')

        project.p('Removed', line)
        msg = f'Removed __version__ from {path.name}'
        project.git.commit(msg, path)


def replace(project):
    path = project.path / (project.name + '.py')
    if not path.exists():
        return

    t = path.read_text()
    b = '.. code-block:: python\n'
    s = t.replace('    ' + b, '').replace(b, '')
    if s == t:
        return

    project.p('Found some rsts')
    path.write_text(s)
    project.git.commit('Get rid of rst code-blocks', path)


def remove_sig(project):
    commits = project.run.out('git', 'l', '-4')
    M = 'Add signature to '
    if M in commits:
        commits = commits.splitlines()
        omit = next(i for i, s in enumerate(commits) if M in s)
        s = 'ac' if omit == 1 else 'b'
        project.git('permute', s)
        project.git('push', '--force-with-lease')


def add_signature(project):
    if not project.is_singleton:
        return

    project.p()

    py_file = (project.path / project.name).with_suffix('.py')
    text = py_file.read_text()
    delim = '"""\n'
    parts = text.split(delim, maxsplit=2)
    # before, comment, after

    if len(parts) == 1:
        project.p('No comments')
        comment, last = '', *parts
    else:
        before, comment, last = parts
        last = before + last
        project.p('before=', bool(before))

    signature = SIGNATURE.format(name=project.name, user=project.user)
    if signature in comment:
        project.p('already signatured')
        return

    comment = comment.rstrip() + signature
    parts = '', comment, last

    py_file.write_text(delim.join(parts))
    project.git.commit('Add signature to ' + py_file.name, py_file)


def add_sponsor_file(project):
    sf = project.path / 'FUNDING.yml'
    if not sf.exists():
        sf.write_text('github: rec\n')
        project.git.commit('Added FUNDING.yml', sf)


SIGNATURE = """

----------

## More info

* [ Code ]( https://github.com/{user}/{name} )
* [ Me ]( https://github.com/rec )
* [ Sponsors ]( https://github.com/sponsors/rec )

"""
