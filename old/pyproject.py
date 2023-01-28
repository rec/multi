
import shutil
import subprocess

NAME = 'pyproject.toml'
SOURCE = '/code/doks/' + NAME


def pyproject(p, source=SOURCE):
    if p.name == 'doks':
        return

    shutil.copyfile(source, p / NAME)
    subprocess.check_output(('git', 'add', NAME), cwd=p)
    subprocess.check_output(
        ('git', 'commit', NAME, '-m', 'Added ' + NAME), cwd=p
    )
