from . import SCRIPTS, configs
from pathlib import Path
import datacls
import shlex
import subprocess

RUN_BASH = str(SCRIPTS / 'run.sh')


@datacls
class Runner:
    path: Path | None = None

    def __call__(self, *args, out=False, complete=False, **kwargs):
        if len(args) == 1:
            args = args[0]
            if isinstance(args, str):
                args = shlex.split(args)
            else:
                assert isinstance(args, (list, tuple)), (args, type(args))
        args = [str(a) for a in args]

        # TODO: this is awful
        if out or complete:
            kwargs.setdefault('stdout', subprocess.PIPE)

        if complete and not out:
            kwargs.setdefault('stderr', subprocess.PIPE)

        kwargs.setdefault('check', not complete)
        kwargs.setdefault('text', True)
        kwargs.setdefault('cwd', self.path)

        if configs.verbose:
            print('$', *args)
        r = subprocess.run(args, **kwargs)
        return (r and r.stdout or '') if out else r

    def out(self, *args, out=True, **kwargs):
        """Run and return stdout as a string on success, else ''"""
        return self(*args, out=out, **kwargs)

    def in_venv(self, *args, **kwargs):
        return self(RUN_BASH, *args, **kwargs)

    def poetry(self, *args, **kwargs):
        return self.in_venv('poetry', '--no-ansi', *args, **kwargs)

    def gh(self, *args, **kwargs):
        return self('gh', *args, **kwargs)

    def commit(self, msg, *files):
        files = [str(i) for i in files]
        self('git', 'add', *files)
        self('git', 'commit', '-m', msg, *files)
        self('git', 'push')
