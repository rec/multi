def refurb(project):
    from .. projects import MULTI

    src = project.name + project.is_singleton * '.py'
    r = MULTI.run('refurb', project.path / src, complete=True)
    result = r.stdout + r.stderr
    if lines := list(_fix_lines(result.splitlines())):
        project.p('Errors', *lines, sep='\n')
        print()


def _fix_lines(lines):
    for line in lines:
        if all(c in line for c in '[]'):
            file_location, line = line.split('[', maxsplit=1)
            _, line = line.split(']', maxsplit=1)
            yield file_location.strip() + line

def _glob(project, *globs):
    return sorted(f for g in globs for f in project.path.glob(g))


def cat(project, *globs):
    for f in _glob(project, *globs):
        print(f'\n{f}:\n{f.read_text().rstrip()}')


def glob(project, *globs):
    project.p(*_glob(project, *globs))


_GREP = 'grep --exclude-dir={build,htmlcov} -nHIR * --include \\*.py -e'


def grep(project):
    project.p()
    try:
        project.run(*_GREP.split(), '__version__')
    except Exception:
        print('---')
        raise
