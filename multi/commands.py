from functools import partial
import tomlkit
import subprocess


def prop(project):
    res = {k: getattr(project, k) for k in project.argv}
    if len(res) == 1:
        res = res.popitem()[1]

    print(f'{project.name:12}:', res)


def status(project):
    if r := project.run_out('git status --porcelain').rstrip():
        print(project.name + ':')
        print(r)


def branch(project):
    print(f'{project.name:12}: {project.branch()}')


def dependencies(project):
    has_deps = len(project.dependencies) > 1
    if has_deps:
        return
    reqs_file = project.path / 'requirements.txt'
    test_reqs_file = project.path / 'test_requirements.txt'
    has_reqs = reqs_file.exists()
    has_test = test_reqs_file.exists()

    for f in reqs_file, test_reqs_file:
        if f.exists():
            print(project.name + ':', f.name)
            with f.open() as fp:
                for line in fp:
                    print('   ', line.strip())
            print()


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
