from functools import partial
import tomlkit
import subprocess


def prop(project):
    res = {k: getattr(project, k) for k in project.argv}
    if len(res) == 1:
        res = res.popitem()[1]

    print(f'{project.name:12}:', res)


def setup(project):
    print('\n', project.name, ':', sep='')
    s = project.run('git status --porcelain')
    if True:
        return print(s)

    lines = [i.strip() for i in s.splitlines()]
    # if 'M setup.py' in lines:



def add_poetry(project):
    p = project.pyproject()

    tool = p.setdefault('tool', {})
    tool['poetry'] = {
        'name': project.name,
        'version': project.version,
        'description': project.description,
        'authors': ['Tom Ritchford <tom@swirly.com>'],
        'license': 'MIT',
        'readme': project.readme, # 'README.md',
        'dependences': {
            'python': project.python_version,
        },
    }

    p['build-system'] = {
        'requires': ['poetry-core'],
        'build-backend': 'poetry.core.masonry.api',
    }

    project.pyproject_file.write_text(tomlkit.dumps(p))
