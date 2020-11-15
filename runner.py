import shlex
import subprocess

PATH = '/Users/tom/.virtualenvs/util/bin'
DRY_RUN = False


def run(lines):
    for line in lines.splitlines():
        if line := line.strip():
            if DRY_RUN:
                print('$', line)
            else:
                subprocess.run(line, shell=True)


def new_version(name, level='patch'):
    return run(f"""
        versy -pe {level}
        rm -Rf build dist
        {PATH}/python setup.py sdist bdist_wheel
        {PATH}/twine check dist/*
        {PATH}/twine upload dist/*
        rm -Rf dist
        open https://github.com/rec/{name}/releases/new""")
