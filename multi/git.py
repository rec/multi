from pathlib import Path
from typing import Callable
import datacls

LOG_FLAGS = '--pretty=format:%h|%cd|%s', '--date=format:%g/%m/%d'


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
            lines = lines.splitlines()
            files = [i.split()[-1] for i in lines]

        files = [Path(f) for f in files]
        if exist := [f for f in files if f.exists()]:
            self('add', *exist, **kwargs)

        self('commit', '-m', msg, *files, **kwargs)
        self('push', **kwargs)

    def commits(self, *args, **kwargs):
        return self('log', *LOG_FLAGS, *args, out=True, **kwargs).splitlines()

    def is_dirty(self, unknown=False, **kwargs):
        lines = self('status', '--porcelain', out=True, **kwargs).splitlines()
        if unknown:
            return any(lines)

        return any(not i.startswith('??') for i in lines)

    def status(self, **kwargs):
        if self.is_dirty():
            self('status', **kwargs)
