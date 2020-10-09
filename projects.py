from pathlib import Path
import functools
import os
import subprocess
import traceback


PROJECTS = sorted(p.parent for p in Path('/code/').glob('*/setup.py'))
CONTINUE_AFTER_FAIL = not False
RUN_ONCE = not True
SKIP = 'backer dedupe hardback scripta'
DRY_RUN = False


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

    return wrapped


if __name__ == '__main__':
    import sys

    _, command, *args = sys.argv
    getattr(__import__(command), command)(*args)
