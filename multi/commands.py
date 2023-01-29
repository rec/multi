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
    direnv = project.path / '.direnv'
    envrc = project.path / '.envrc'

    if direnv.exists() and envrc.exists():
        return

    gitignore = project.path / '.gitignore'
    contents = gitignore.read_text() + '\n.direnv\n.envrc\n'
    gitignore.write_text(contents)
    msg = 'Add .direnv, .envrc to .gitignore'
    project.run('git', 'commit', '.gitignore', '-m', msg)
    project.run('git', 'push')

    print(f'{project.name:10}:')
