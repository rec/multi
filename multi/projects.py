from . import ROOT
from . project import Project
import copy
import tomlkit

FILE = ROOT / 'multi.toml'
BACK_FILE = FILE.with_suffix('.bak.toml')
DATA = tomlkit.loads(FILE.read_text())
BACK = copy.deepcopy(DATA)
_RANKED = DATA['ranked']

PROJECTS = {k: Project(k, i) for i, k in enumerate(_RANKED)}

MULTI = PROJECTS['multi']
REC = Project('rec', len(PROJECTS))

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
    if BACK != DATA:
        if BACK:
            _write_one(BACK_FILE, BACK)
            BACK.clear()

        _write_one(FILE, DATA)
