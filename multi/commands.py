from functools import partial
import tomlkit
import subprocess


def prop(project):
    res = {k: getattr(project, k) for k in project.argv}
    if len(res) == 1:
        res = res.popitem()[1]

    print(f'{project.name:12}:', res)


def setup(project):
    s = project.run_out('git status --porcelain')
    lines = [i.strip() for i in s.splitlines()]
    if 'M setup.py' in lines:
        msg = 'Add icons to description in setup.py'
        project.run('git', 'commit', 'setup.py', '-m', msg)
        project.run('git', 'push')


def status(project):
    if r := project.run_out('git status --porcelain').rstrip():
        print(project.name + ':')
        print(r)


def main(project):
    try:
        project.run('git checkout main')
    except Exception:
        project.run('git checkout master')


def branch(project):
    print(f'{project.name:12}: {project.branch()}')


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
