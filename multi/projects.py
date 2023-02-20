from . import ROOT
from . project import Project
import copy
import tomlkit

MULTI_FILE = ROOT / 'multi.toml'
MULTI_BACK_FILE = MULTI_FILE.with_suffix('.bak.toml')
MULTI_DATA = tomlkit.loads(MULTI_FILE.read_text())
MULTI_BACK = copy.deepcopy(MULTI_DATA)
PROJECTS_DATA = MULTI_DATA.setdefault('project', {})
RANKED = MULTI_DATA['ranked']
PROJECTS = {k: Project(k, PROJECTS_DATA[k], i) for i, k in enumerate(RANKED)}


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


def color(rank):
    return COLORS[rank % len(COLORS)]


def _write_one(p, d):
    p.write_text(tomlkit.dumps(d))


def write():
    if MULTI_BACK != MULTI_DATA:
        if MULTI_BACK:
            _write_one(MULTI_BACK_FILE, MULTI_BACK)
            MULTI_BACK.clear()

        _write_one(MULTI_FILE, MULTI_DATA)
