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
