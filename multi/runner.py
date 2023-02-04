from . import configs
import subprocess
from pathlib import Path
import datacls
import shlex

SCRIPTS = Path(__file__).parents[1] / 'scripts'
RUN_BASH = str(SCRIPTS / 'run.sh')


@datacls
class Runner:
    path: Path | None = None

    def __call__(self, *args, out=False, arm=True, **kwargs):
        if len(args) == 1:
            args = args[0]
            if isinstance(args, str):
                args = shlex.split(args)
        args = [str(a) for a in args]

        if out:
            kwargs.setdefault('stdout', subprocess.PIPE)

        kwargs.setdefault('check', True)
        kwargs.setdefault('text', True)
        kwargs.setdefault('cwd', self.path)

        if arm:
            args = 'arch', '-arm64', *args

        if configs.verbose:
            print('$', *args)
        r = subprocess.run(args, **kwargs)
        if not out:
            return r
        elif r:
            return r.stdout
        else:
            return ''

    def out(self, *args, out=True, **kwargs):
        """Run and return stdout as a string on success, else ''"""
        return self(*args, out=out, **kwargs)

    def in_venv(self, *args, **kwargs):
        return self(RUN_BASH, *args, **kwargs)

    def poetry(self, *args, **kwargs):
        return self.in_venv('poetry', '--no-ansi', *args, **kwargs)

    def gh(self, *args, **kwargs):
        return self.run('gh', *args, **kwargs)

    def commit(self, msg, *files):
        files = [str(i) for i in files]
        self('git', 'add', *files)
        self('git', 'commit', '-m', msg, *files)
        self('git', 'push')
