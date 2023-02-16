from . project import Project

NAMES = [
    'abbrev',
    'backer',
    'blocks',
    'cfgs',
    'datacls',
    'def_main',
    'dek',
    'dtyper',
    'editor',
    'gitz',
    'hardback',
    'impall',
    'loady',
    'multi',
    'nc',
    'nmr',
    'plur',
    'runs',
    'safer',
    'sproc',
    'tdir',
    'vl8',
    'wavemap',
    'xmod',
]

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


PROJECTS = {k: Project(k, i) for i, k in enumerate(NAMES)}
MULTI = PROJECTS['multi']


def color(name):
    return COLORS[RANK.index(name) % len(COLORS)]


def write_projects(path):
    d = {p.name: {'index': p.index, **p.multi} for p in PROJECTS.values()}

    import tomlkit

    path.write_text(tomlkit.dumps(d))


if __name__ == '__main__':
    from pathlib import Path

    write_projects(Path(__file__).parents[1] / 'projects.toml')
