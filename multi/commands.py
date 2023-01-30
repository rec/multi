from functools import partial
from pathlib import Path
import tomlkit
import shlex
import subprocess

ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / 'scripts'
RUN_SH = str(SCRIPTS / 'run.sh')


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


def run(project):
    print(project.name + ':')
    project.run(*project.argv)
    print()


def run_in(project):
    print(project.name + ':')
    project.run(RUN_SH, *project.argv)
    print()


def bash(project):
    print(project.name + ':')
    project.run('bash', '-c', shlex.join(project.argv))
    print()


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
