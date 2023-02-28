from .. import configs, projects, project
import functools
import re
import requests
import safer

CATEGORIES = 'production', 'beta', 'experimental', 'mothballed'
REC = project.Project('rec', len(projects.PROJECTS))
LOG_FLAGS = '--pretty=format:%h|%cd|%s', '--date=format:%g/%m/%d'
"""
Per project data:

description (🌟 # if # > 1)
Release v1.0.2:  [date] [message]
Latest commit:  [date] [message]

"""


def _a(href, contents):
    return f'<a href="{href}">{contents}</a>'


def _commit(project, label, log):
    commit_id, date, message = (p.strip() for p in log.split('|', maxsplit=2))

    url = f'{project.git_url}/commit/{commit_id}'
    link = _a(url, f'<code>{date}</code>')

    return f'{link}{label}<code>{message}</code>'


def _pad(line, amount=105, offset=0):
    count = offset + (amount - len(line)) // 2
    spaces = count * '&nbsp;'
    return spaces + line


_COUNT_OFFSETS = {
    'blocks': -12,
    'plur': -2,
    'nmr': -2,
    'wavemap': +2,
}


def summary(project):
    e1, desc, e2 = project.description_parts
    name = f'<code>{project.name}</code>'
    link = _a(project.git_url, name)

    try:
        stars = project.github_info['stargazers_count']
    except KeyError:
        print(project.github_info)
        raise
    star = stars > 1 and f' (🌟 {stars})' or ''

    offset = _COUNT_OFFSETS.get(project.name, 0)
    desc_line = _pad(f'{e1} {link} {e2}' + star, offset=offset)
    desc_line2 = _pad(f'<i>{desc}</i>', 55)

    commits = project.git('log', *LOG_FLAGS, out=True).splitlines()
    latest_line = _commit(project, '🕰', commits[0])

    if commit := next((c for c in commits if VERSION(c)), None):
        release_line = _commit(project, f'🟢', commit)
    else:
        release_line = ''

    lines = desc_line, desc_line2, release_line, latest_line
    summary = '\n<br>\n'.join(lines)
    return summary


def _cell(project):
    cell = summary(project)
    return f'<td>{cell}</td>'


def _row(projects):
    cells = '\n'.join(_cell(p) for p in projects)
    return f'<tr>{cells}</tr>'


def make_table(name, projects):
    pairs = (projects[i: i + 2] for i in range(0, len(projects), 2))
    body = '\n'.join(_row(p) for p in pairs)

    label = f'<h2>{name.capitalize()}</h2>\n'
    return f'{label}<table><tbody>{body}</tbody></table>'


VERSION = re.compile(r'ersion v\d+\.\d+\.\d+$').search


def rec():
    categories = {c: [] for c in CATEGORIES}
    tags = projects.DATA['tags']
    for p in projects.PROJECTS.values():
        for c in CATEGORIES:
            if p.name in tags[c]:
                categories[c].append(p)

    tables = (make_table(k, v) for k, v in categories.items())
    result = '\n<p>\n'.join(tables)
    (REC.path / 'README.md').write_text('# Tom Ritchford\n' + result)
    REC.git('commit', '--amend', 'README.md', '--no-edit')
    REC.git('push', '-f')


def filename(project):
    return project.path / 'README.md'


def readme(project):
    project.p(filename(project).open().readline())
    project.write_pyproject()


def _write_readme(project):
    url = f'https://rec.github.io/{project.name}'
    anchor = project.api_anchor
    link = f'\n\n### [API Documentation]({url}#{anchor})\n'

    with safer.open(filename(project), 'w') as fp:
        fp.write(project.comment)
        fp.write(link)


def write_readme(project):
    fname = filename(project)
    contents = fname.read_text()

    _write_readme(project)

    if configs.push and contents != fname.read_text():
        project.git.commit(f'Update README.md from {project.name}.py', fname)
