import info
import subprocess


def pusher(p):
    subprocess.run(('git', 'push'))
