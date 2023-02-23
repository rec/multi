import subprocess
from pathlib import Path
from typing import Callable
import datacls


@datacls
class Git:
    run: Callable

    def __call__(self, *a, **ka):
        return self.run('git', *a, **ka)

    def commit(self, msg, *files, **kwargs):
        if not self.is_dirty(**kwargs):
            return

        if not files:
            lines = self('status', '--porcelain', out=True, **kwargs)
            files = [i.split()[-1] for i in lines.splitlines()]

        files = [Path(f) for f in files]
        if exist := [f for f in files if f.exists()]:
            self('add', *exist, **kwargs)

        self('commit', '-m', msg, *files, **kwargs)
        self('push', **kwargs)

    def is_dirty(self, **kwargs):
        lines = self('status', '--porcelain', out=True).splitlines()
        return any(not i.startswith('??') for i in lines)

    def status(self):
        if self.is_dirty():
            self('status')
