from .. import configs, projects
from pathlib import Path
import threading
import time
import subprocess
import sys

PYPROJECT = 'pyproject.toml'
PROJECT_FILES = 'poetry.lock', PYPROJECT
NONE = object()
MKDOCS = Path(__file__).parents[1] / 'mkdocs'
DRY_RUN = True
MKDOCS_BINARY = str(projects.MULTI.bin_path / 'mkdocs')
RENAMED = 'backer', 'def_main', 'hardback', 'impall', 'nc', 'nmr', 'vl8'

assert configs


def add_mkdocs(project, *argv):
    if (project.path / 'doc').exists():
        return
    docs = sorted(i for i in MKDOCS.rglob('*') if not i.name.startswith('.'))

    written = [f for d in docs for f in _write_doc(project, d)]
    assert written
    project.run(MKDOCS_BINARY, 'build')
    msg = 'Add mkdocs documentation'
    project.git.commit(msg, *written)


def _write_doc(project, doc):
    if doc.is_dir():
        return

    contents = doc.read_text()
    if '.tpl' in doc.suffixes:
        contents = contents.format(project=project)

        suffixes = ''.join(s for s in doc.suffixes if s != '.tpl')
        while doc.suffix:
            doc = doc.with_suffix('')
        doc = doc.with_suffix(suffixes)

    rel = project.path / doc.relative_to(MKDOCS)
    rel.parent.mkdir(exist_ok=True)
    rel.write_text(contents)
    yield rel


def fix_gitignore(project):
    gi = project.path / '.gitignore'
    lines = gi.read_text().splitlines()
    if 'site/' in lines:
        return
    if matches := [i for i, line in enumerate(lines) if line == '/site']:
        for i in matches:
            lines[i] = 'site/'
        msg = 'Replaced /site with site/ in .gitignore'
    else:
        lines.append('site/')
        msg = 'Added site/ to .gitignore'

    gi.write_text('\n'.join(lines) + '\n')
    project.git.commit(msg, gi)
    project.p(gi, '/site -> site/')


def remove_tag(project, *tags):
    removed = False
    for tag in tags:
        try:
            project.tags.remove(tag)
            removed = True
        except ValueError:
            pass

    if removed:
        if not project.tags:
            del project.poetry['tags']
        project.write()
        project.p('Tags:', *project.tags)


def add_tag(project, *tags):
    if tags:
        with project.writer():
            project.tags.extend(tags)
            msg = f'Set multi.tags to {", ".join(tags)} in {PYPROJECT}'
        project.git.commit(msg, PYPROJECT)
        project.p('Tags:', *project.tags)


def open_readme(project):
    if project.branch() == 'rst-to-md':
        print(project.name + ':')
        project.open_git()
        project.open_git('tree/rst-to-md')


def readme(project):
    if files := sorted(project.path.glob('README.*')):
        project.run('wc', '-l', *files)


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


def tweak_github(project):
    project.run.gh(
        'repo',
        'edit',
        '--enable-merge-commit=false',
        '--enable-rebase-merge',
        '--enable-squash-merge=false',
    )
    project.p()


def bump_version(project, rule_or_version, *notes):
    project.run.poetry('version', rule_or_version)
    project.reload()

    version = 'v' + project.poetry['version']
    project.git.commit(f'Update to version {version}', PYPROJECT)
    project.git('tag', version)
    project.git('push', '--tag', '--force-with-lease')
    notes = ' '.join(notes).strip() or f'Version {version}'
    project.run.gh('release', 'create', '--notes', notes)


def get(project, address, *args):
    data = _getattrs(project, [address])

    if not callable(data):
        project.p(data)
        return

    try:
        result = data(*args)
    except Exception as e:
        result = e

    if not isinstance(result, (type(None), subprocess.CompletedProcess)):
        print(result)
    print()


def assign(project, *argv):
    parts = [(k, v) for a in argv for k, _, v in a.partition('=')]
    if bad := sorted(a for a, (k, v) in zip(argv, parts) if not (k and v)):
        raise ValueError(f'No assignments in {bad}')

    with project.writer() as multi:
        for k, v in parts:
            *rest, last = k.split('.')
            m = multi
            for i in rest:
                m = m.setdefault(i, {})
            m[last] = v


def run(project, *argv):
    project.p()
    project.run(*argv)
    print()


def bash(project, *argv):
    project.p()
    project.run.bash(*argv)
    print()


def single(project, *argv):
    if project.is_singleton:
        print(project.name + ':')


def run_poetry(project, *argv):
    print(project.name + ':')
    project.run.poetry(*argv)
    print()


def serve(project, *args):
    if project.is_singleton:
        args = '-w', project.name + '.py', *args

    args = MKDOCS_BINARY, 'serve', f'--dev-addr={project.server_url}', *args
    threading.Thread(target=project.run, args=args, daemon=True).start()

    time.sleep(0.5)
    project.open_server()
    return True


def _exit(*args):
    # Elsewhere.
    if args:
        print(*args, file=sys.stderr)
        exit(-1)
    exit(0)


def _getattr(data, a):
    for part in a and a.split('.'):
        try:
            data = data[part]
        except Exception:
            try:
                data = getattr(data, part)
            except AttributeError:
                return
    yield data


def _getattrs(data, argv):
    result = {a: d for a in argv or [''] for d in _getattr(data, a)}

    if len(result) == 1 and len(argv) == 1:
        return result.popitem()[1]
    return result
