from bs4 import BeautifulSoup
from projects import over_projects
from versy.version_file import version_file
import re
import requests
import subprocess

RELEASE_RE = re.compile(r'Version v(\d+\.\d+\..+)')


def pypi_version(p):
    page = requests.get(f'https://pypi.org/project/{p.name}')
    if page.status_code != 200:
        return
    soup = BeautifulSoup(page.text)
    version, = soup.find_all('h1', {'class': 'package-header__name'})

    project, version_number = version.text.strip().split()
    assert project == p.name
    return version_number


def is_dirty():
    return bool(subprocess.run('git --quiet HEAD --'.split()).returncode)


def local_version(p):
    try:
        return version_file(p, None)[0]
    except Exception:
        return


def top_version_if_any():
    lines = subprocess.check_output('git log --oneline -1'.split())
    assert len(lines) == 1
    _, message = lines[0].split(maxsplit=1)
    return (m := RELEASE_RE.match(message)) and m.groups(1)


@over_projects
def info(p):
    print(
        pypi_version(p),
        is_dirty(),
        local_version(p),
        top_version_if_any,
    )
