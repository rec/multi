import re
import safer
from projects import over_projects

LANGUAGE = re.compile(r"'Programming Language :: Python :: (\d)\.(\d)'")


@over_projects
def update_setup(p):
    setup = p / 'setup.py'
    latest = None

    with safer.writer(setup) as write:
    print(setup)
    for line in setup.open():
        if (match := LANGUAGE.search(line)):
            print(*match.groups())
        else:
            pass
        # write(line)


if __name__ == '__main__':
    update_setup()
