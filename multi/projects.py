from . import ROOT
from . project import Project
import copy
import tomlkit

PROJECTS_FILE = ROOT / 'projects.toml'
PROJECTS_BACK_FILE = PROJECTS_FILE.with_suffix('.toml.bak')
PROJECTS_DATA = tomlkit.loads(PROJECTS_FILE.read_text())
PROJECTS_BACK = copy.deepcopy(PROJECTS_DATA)

PROJECTS = {k: Project(k, v) for k, v in PROJECTS_DATA.items()}
MULTI = PROJECTS['multi']


def add_rank():
    for i, name in enumerate(RANK):
        PROJECTS[name].data['rank'] = i

    write_projects()


RANK = [
    'safer',
    'tdir',
    'dtyper',
    'wavemap',
    'editor',
    'datacls',
    'xmod',
    'impall',
    'gitz',
    'nmr',
    'nc',
    'abbrev',
    'plur',
    'sproc',
    'def_main',
    'dek',
    'blocks',
    'multi',
    'hardback',
    'loady',
    'runs',
    'cfgs',
    'backer',
    'vl8',
]

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
    return COLORS[product.index % len(COLORS)]


def _write_one(p, d):
    p.write_text(tomlkit.dumps(d))


def write_projects():
    if PROJECTS_BACK != PROJECTS_DATA:
        if PROJECTS_BACK:
            _write_one(PROJECTS_BACK_FILE, PROJECTS_BACK)
            PROJECTS_BACK.clear()

        _write_one(PROJECTS_FILE, PROJECTS_DATA)


if __name__ == '__main__':
    add_rank()
