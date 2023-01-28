from pathlib import Path
import functools
import os
import subprocess
import traceback


PROJECTS = sorted(p.parent for p in Path('/code/').glob('*/setup.py'))
CONTINUE_AFTER_FAIL = not False
RUN_ONCE = not True
DRY_RUN = not True


def run(*cmd):
    print('$', *cmd)
    if not DRY_RUN:
        if (code := subprocess.run(cmd).returncode):
            raise ValueError('Ooops', str(code))


def over_projects(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        results = []
        for p in PROJECTS:
            os.chdir(p)
            try:
                results.append(f(p, *args, **kwargs))
            except Exception:
                if not CONTINUE_AFTER_FAIL:
                    raise
                traceback.print_exc()

            if RUN_ONCE:
                break

    wrapped._over = True

    return wrapped


if __name__ == '__main__':
    import sys

    _, command, *args = sys.argv
    func = getattr(__import__(command), command)
    if not getattr(func, '_over', False):
        func = over_projects(func)
    func(*args)
