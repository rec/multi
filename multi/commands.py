from functools import partial
import tomlkit
import subprocess

run = partial(subprocess.run, text=True, check=True)



def name(project):
    print(project.name)


def version(project):
    print(f'{project.name:12}: {project.version()}')


def add_poetry(project):
    p = project.pyproject()

    tool = p.setdefault('tool', {})
    tool['poetry'] = {
        'name': project.name,
        'version': '{version}',
        'description': '{description}',
        'authors': ['Tom Ritchford <tom@swirly.com>'],
        'license': 'MIT',
        'readme': 'README.md',
        'dependences': {
            'python': '^{python_version}',
        },
    }

    p['build-system'] = {
        'requires': ['poetry-core'],
        'build-backend': 'poetry.core.masonry.api',
    }

    project.pyproject_file.write_text(tomlkit.dumps(p))
