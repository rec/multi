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


def add_signature(project):
    if not project.is_singleton:
        return

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

    signature = SIGNATURE.format(name=project.name)
    parts = '', comment + signature, last

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

* [ Code ]( https://github.com/rec/abbrev )
* [ Docs ]( https://rec.github.io/abbrev )
* [ Me ]( https://github.com/rec )
* [ Sponsors ]( https://github.com/sponsors/rec )

"""
