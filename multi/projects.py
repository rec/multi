from . import ROOT
from . project import Project
import copy
import tomlkit

PROJECTS_FILE = ROOT / 'multi.toml'
PROJECTS_BACK_FILE = PROJECTS_FILE.with_suffix('.bak.toml')
PROJECTS_DATA = tomlkit.loads(PROJECTS_FILE.read_text())
PROJECTS_BACK = copy.deepcopy(PROJECTS_DATA)

_PROJECTS = [Project(k, v) for k, v in PROJECTS_DATA.items()]
_PROJECTS.sort(key=lambda p: p.data['rank'])
PROJECTS = {p.name: p for p in _PROJECTS}


MULTI = PROJECTS['multi']

COLORS = [
    'red',
    'pink',
    'purple',
    'deepPurple',
    'indigo',
    'blue',
    'lightBlue',
    'cyan',
    'teal',
    'green',
    'lightGreen',
    'lime',
    'yellow',
    'amber',
    'orange',
    'deepOrange',
    'black',
    'brown',
    'grey',
    'blueGrey',
    'white',
]


def color(project):
    return COLORS[project.index % len(COLORS)]


def _write_one(p, d):
    p.write_text(tomlkit.dumps(d))


def write():
    if PROJECTS_BACK != PROJECTS_DATA:
        if PROJECTS_BACK:
            _write_one(PROJECTS_BACK_FILE, PROJECTS_BACK)
            PROJECTS_BACK.clear()

        _write_one(PROJECTS_FILE, PROJECTS_DATA)
