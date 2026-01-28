from . project import DATA, Project
import copy
import tomlkit

BACK = copy.deepcopy(DATA)
PROJECTS = {name: Project(name, tag, i) for i, (name, tag) in enumerate(DATA['ranked'])}

MULTI = PROJECTS['multi']
REC = Project('rec', len(PROJECTS))
GITHUB_IO = Project('rec.github.io', len(PROJECTS))

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
