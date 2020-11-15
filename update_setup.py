import info
import runner
import safer
import subprocess

MARKER = 'Development Status :: '
BETA = '4 - Beta'
PRODUCTION = '5 - Production/Stable'


def update_setup(p):
    if not info.is_dirty():
        return

    version = info.top_version_if_any() or info.local_version(p)
    if not version or version[0] < '1':
        return

    print(f'{p.name:8} {version:6}')
    runner.run("""
        git commit setup.py -m "Update setup.py to Production/Stable"
        git push""")

    runner.new_version(p.name)


def _old(version, p):
    setup = p / 'setup.py'
    line = next((i for i in setup.open() if MARKER in i), None)
    if not line or PRODUCTION in line:
        return

    line = line.split(MARKER)[-1].strip()
    print(f'{p.name:8} {version:6} {line}')

    with safer.open(setup, 'w') as writer, setup.open() as reader:
        for line in reader:
            if MARKER in line:
                old, line = line, line.replace(BETA, PRODUCTION)
                assert old != line, f'{old=} {line=}'
            writer.write(line)
