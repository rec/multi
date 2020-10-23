from bs4 import BeautifulSoup
from projects import over_projects
from versy.version_file import get_version_file
import re
import requests
import subprocess

RELEASE_RE = re.compile(r'Version v(\d+\.\d+\..+)')


def strip_quotes(q):
    if True:
        return q
    return q[1:-1] if (len(q) > 1 and q[0] == q[-1] and q[0] in '"\'') else q


@over_projects
def info(p):
    star = '*' if is_dirty() else ''
    pypi = pypi_version(p)
    top = top_version_if_any()
    local = local_version(p)

    if pypi:
        if pypi == top:
            needs = ''
        elif top == local:
            needs = '^'
        else:
            needs = '!'
        print(f'{p.name}{star}: {pypi}{needs}')
    else:
        print(f'{p.name}{star}: ({local})')


@over_projects
def info2(p):
    print(local_version(p))


def pypi_version(p):
    page = requests.get(f'https://pypi.org/project/{p.name}')
    if page.status_code != 200:
        return

    soup = BeautifulSoup(page.text, 'html.parser')
    version, = soup.find_all('h1', {'class': 'package-header__name'})

    project, version_number = version.text.strip().split()
    assert project == p.name
    return strip_quotes(version_number)


def is_dirty():
    cmd = 'git diff-index --quiet HEAD --'.split()
    return bool(subprocess.run(cmd).returncode)


def local_version(p):
    try:
        return strip_quotes(get_version_file(None, p)[0])
    except Exception:
        return


def top_version_if_any():
    output = subprocess.check_output('git log --oneline -1'.split()).decode()
    lines = output.splitlines()
    assert len(lines) == 1
    _, message = lines[0].split(maxsplit=1)
    if (m := RELEASE_RE.match(message)):
        return strip_quotes(m.group(1))
