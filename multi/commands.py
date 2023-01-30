from functools import partial
import tomlkit
import shlex
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


def run(project):
    print(project.name + ':')
    project.run(*project.argv)
    print()


def run_in(project):
    print(project.name + ':')
    project.run_in(*project.argv)
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
    if has_deps:
        return

    reqs_file = project.path / 'requirements.txt'
    test_reqs_file = project.path / 'test_requirements.txt'

    parts = ['pyproject.toml', 'poetry.lock']
    if r := list(_read_req(reqs_file, project.python_version)):
        project.poet('add', *r)
        reqs_file.unlink()
        parts.append(str(reqs_file))

    if s := list(_read_req(test_reqs_file, project.python_version)):
        project.poet('add', '--dev', *s)
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
