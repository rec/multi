import info

MARKER = 'Development Status :: '


def update_setup(p):
    version = info.top_version_if_any() or info.local_version(p)
    setup = p / 'setup.py'
    if line := next((i for i in setup.open() if MARKER in i), None):
        line = line.split(MARKER)[-1].strip()
        print(f'{p.name:8} {version:6} {line}')
