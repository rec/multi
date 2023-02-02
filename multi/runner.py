import subprocess
from pathlib import Path
import datacls

SCRIPTS = Path(__file__).parents[1] / 'scripts'
RUN_BASH = str(SCRIPTS / 'run.sh')


@datacls
class Runner:
    path: Path | None = None

    def __call__(self, *args, out=False, **kwargs):
        if out:
            kwargs.setdefault('stdout', subprocess.PIPE)

        kwargs.setdefault('check', True)
        kwargs.setdefault('text', True)
        kwargs.setdefault('cwd', self.path)

        if len(args) == 1 and isinstance(args[0], str):
            args = args[0].split()

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

    def bash(self, *args, **kwargs):
        return self(RUN_BASH, *args, **kwargs)

    def arm(self, *args, **kwargs):
        return self.bash('arch', '-arm64', *args, **kwargs)

    def poetry(self, *args, **kwargs):
        return self.arm('poetry', '--no-ansi', *args, **kwargs)

    def commit(self, msg, *files):
        files = [str(i) for i in files]
        self('git', 'add', *files)
        self('git', 'commit', '-m', msg, *files)
        self('git', 'push')
