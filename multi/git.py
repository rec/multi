import subprocess
from typing import Callable
import datacls


@datacls
class Git:
    run: Callable

    def __call__(self, *a, **ka):
        return self.run('git', *a, **ka)

    def commit(self, msg, *files):
        if exist := [f for f in files if f.exists()]:
            self('add', *exist)

        self('commit', '-m', msg, *files)
        self('push')

    @property
    def is_dirty(self):
        try:
            self('diff-index', '--quiet', 'HEAD', '--')
            return False
        except subprocess.CalledProcessError:
            return True

    def status(self):
        if self.is_dirty:
            self('status')
