def get_stars(project):
    import re
    # DOES NOT WORK (need to render JS)
    # Star this repository (361962)

    def get_page(project):
        return requests.get(project.git_url).text

    STARS_RE = re.compile(r'="Star this repository \((\d+)\)"')

    if m := STARS_RE.match(get_page(project)):
        project.p(int(m.group(1)))
    project.p('No stars')


def fix_readme(project):
    project.p(project.poetry['readme'])
    if project.poetry['readme'].endswith('.me'):
        project.poetry['readme'] = 'README.md'
        project.write_pyproject()
        project.git.commit('Fix typo in pyproject.toml', 'pyproject.toml')


def rename_readme(project):
    if not project.poetry['readme'].endswith('.rst'):
        return

    project.git('mv', 'README.rst', 'README.md')

    _write_readme(project)

    project.poetry['readme'] = 'README.md'
    project.write_pyproject()
    msg = 'Rename README.rst to README.md'
    project.git.commit(msg, 'README.rst', 'README.md', 'pyproject.toml')
    project.open_git()


def old_grep(project):
    project.p()
    filename = project.name + '.py'
    re = r'\.\. code-block:: python'
    try:
        project.run('grep', '-e', re, filename)
    except Exception:
        print('---')


def list_to_log(project):
    if files := list(project.path.glob('CHANGE*')):
        project.p(*files)


def clean_ranks():
    from .. import projects

    rank = [p.name for p in projects.PROJECTS.values()]
    projects.DATA['rank'] = rank
    projects.write()


def clean_dir(project):
    print(f'cd {project.path}')
    print('direnv reload')
    print('poetry --no-ansi install')


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


NONE = object()
DRY_RUN = True


def old_files(project):
    if files := _glob(project, 'setup.*', 'MANIFEST*', 'requirements*.txt'):
        if True:
            _p(project, *files)
            return
        project.git('rm', *files)
        project.git.commit('Remove old files', *files)
        _p(project, 'Removed', *files)


def fix_desc(project):
    import pyperclip as pc
    pc.copy(project.poetry['description'])
    project.open_git()
    input('Press return to continue')


EMOJIS = {
    'datacls': '🗂',
    'def_main': '🗣',
    'hardback': '📓',
    'impall': '🛎',
    'loady': '🛍',
    'nmr': '🌐',
    'multi': '📚',
}

DESCS = {
    'blocks':  'Solve a block puzzle',
    'cfgs':  'XDG standard config files',
    'datacls':  'Adds a little to dataclasses',
    'def_main':  'A decorator for main',
    'dek':  'The decorator-decorator',
    'dtyper':  'Call or make dataclasses from `typer` commands',
    'editor':  'Open the default text editor',
    'gitz':  'Tiny useful git commands, some dangerous',
    'hardback':  'Hardcopy backups of digital data',
    'impall':  'Test-import all modules below a given root',
    'loady':  'Load Python code and data from git',
    'multi':  'Manage all my other projects',
    'nmr':  'Name all canonical things',
    'plur':  'Simple universal word pluralizer',
    'runs':  'Run a block of text as a subprocess',
    'safer':  'A safer file opener',
    'sproc':  'Subprocesseses for subhumanses',
    'tdir':  'Create and fill a temporary directory',
    'vl8':  'Perturbed audio',
    'xmod':  'Turn an object into a module',
}


def fix_desc(project):
    desc = project.poetry['description'].strip()

    items = list(enumerate(desc))
    begin = next(i for i, c in items if c.isascii())
    end = next(i for i, c in reversed(items) if c.isascii())

    if begin:
        e1 = desc[:begin].strip()
        e2 = desc[end + 1:].strip()
        desc = desc[begin:end + 1].strip()
    else:
        e1 = e2 = EMOJIS[project.name]

    desc = DESCS.get(project.name, desc)
    desc = f'{e1} {desc} {e2}'
    if project.poetry['description'] == desc:
        return

    _p(project, 'Changed:', desc)
    project.poetry['description'] = desc
    project.write()
    project.run.poetry('lock')
    msg = 'Standardize project description'
    project.git.commit(msg, 'pyproject.toml', *PROJECT_FILES)


def setup(project):
    s = project.run_out('git status --porcelain')
    lines = [i.strip() for i in s.splitlines()]
    if 'M setup.py' in lines:
        msg = 'Add icons to description in setup.py'
        project.run('git', 'commit', 'setup.py', '-m', msg)
        project.run('git', 'push')


def main(project):
    try:
        project.run('git checkout main')
    except Exception:
        project.run('git checkout master')


def rename_main(project):
    if project.branch() == 'main':
        return

    project.run('git branch -m master main')
    project.run('git fetch -p origin')
    project.run('git branch -u origin/main main')
    project.run('git remote set-head origin -a')


def add_poetry(project):
    p = project.pyproject

    tool = p.setdefault('tool', {})
    if 'poetry' in tool:
        return

    tool['poetry'] = {
        'name': project.name,
        'version': project.version,
        'description': project.description,
        'authors': ['Tom Ritchford <tom@swirly.com>'],
        'license': 'MIT',
        'readme': project.readme, # 'README.md',
        'dependencies': {
            'python': project.python_version,
        },
    }

    p['build-system'] = {
        'requires': ['poetry-core'],
        'build-backend': 'poetry.core.masonry.api',
    }

    file = project.pyproject_file
    file.write_text(tomlkit.dumps(p))
    project.run('poetry lock')

    files = 'poetry.lock', 'pyproject.toml'
    project.run('git', 'add', *files)
    msg = f'Teach {project.name} about poetry'
    project.run('git', 'commit', '-m', msg, *files)
    project.run('git', 'push')


def add_dotenv(project):
    import os

    direnv = project.path / '.direnv'
    envrc = project.path / '.envrc'

    if direnv.exists() and envrc.exists():
        return

    print('cd', project.path)
    if True:
        return

    print(f'{project.name:10}:')

    project.run('direnv allow')
    cmd = f'cd {project.path} && direnv exec {project.path} poetry install'
    cmd = f'direnv exec {project.path} which python'
    #project.run('bash', '-c', cmd, cwd=os.getcwd())
    project.run(cmd)


def dependencies(project):
    has_deps = len(project.dependencies) > 1
    if has_deps:
        return
    reqs_file = project.path / 'requirements.txt'
    test_reqs_file = project.path / 'test_requirements.txt'
    test_reqs_file2 = project.path / 'test-requirements.txt'
    has_reqs = reqs_file.exists()
    has_test = test_reqs_file.exists()

    for f in reqs_file, test_reqs_file, test_reqs_file2:
        if f.exists():
            print(project.name + ':', f.name)
            with f.open() as fp:
                for line in fp:
                    print('   ', line.strip())
            print()


def add_dependencies(project):
    print(project.name + ':')
    has_deps = len(project.dependencies) > 1
    if has_deps and False:
        return

    reqs_file = project.path / 'requirements.txt'
    test_reqs_file = project.path / 'test_requirements.txt'

    print(test_reqs_file, test_reqs_file.exists())
    parts = ['pyproject.toml', 'poetry.lock']
    if r := list(_read_req(reqs_file, project.python_version)):
        project.poetry('add', *r)
        reqs_file.unlink()
        parts.append(str(reqs_file))

    if s := list(_read_req(test_reqs_file, project.python_version)):
        project.poetry('add', '--dev', *s)
        test_reqs_file.unlink()
        parts.append(str(test_reqs_file))

    if r or s:
        msg = 'Bring requirements into poetry'
        project.run('git', 'commit', *parts, '-m', msg)
        project.run('git', 'push')


def add_d(project):
    has_deps = len(project.dependencies) > 1
    if has_deps:
        return

    reqs_file = project.path / 'requirements.txt'
    test_reqs_file = project.path / 'test_requirements.txt'

    parts = ['pyproject.toml', 'poetry.lock']
    if r := list(_read_req(reqs_file, project.python_version)):
        print(reqs_file)
        print(r)
        print()

    if s := list(_read_req(test_reqs_file, project.python_version)):
        print(test_reqs_file)
        print(s)
        print()


def list_d(project):
    reqs_file = project.path / 'requirements.txt'
    test_reqs_file = project.path / 'test_requirements.txt'
    re, te = reqs_file.exists(), test_reqs_file.exists()
    if re or te:
        print(project.name, re, te)


def _read_req(p, python_version):
    if not p.exists():
        return

    to_delete = 'doks', 'versy'
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and line not in to_delete:
            if line == 'flake8' and python_version.endswith('3.7'):
                line = 'flake8@5.0.4'
            yield line
