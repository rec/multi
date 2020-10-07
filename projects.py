from pathlib import Path
import functools
import os
import traceback

PROJECTS = sorted(p.parent for p in Path('/code/').glob('*/setup.py'))
CONTINUE_AFTER_FAIL = False


def over_projects(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        results = []
        for p in PROJECTS:
            os.chdir(p)
            try:
                results.append(f(p, *args, **kwargs))
            except Exception:
                if CONTINUE_AFTER_FAIL:
                    raise
                traceback.print_exc()

    return wrapped
