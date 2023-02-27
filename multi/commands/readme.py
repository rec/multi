from .. import configs, projects, project
import functools
import re
import requests
import safer

CATEGORIES = 'production', 'beta', 'experimental', 'mothballed'
REC = project.Project('rec', len(projects.PROJECTS))
LOG_FLAGS = '--pretty=format:%h|%cd|%s', '--date=format:%C/%m/%d-%H:%M'
"""
Per project data:

description (🌟 # if # > 1)
Release v1.0.2:  [date] [message]
Latest commit:  [date] [message]

"""


def _a(href, contents):
    return f'<a href="{href}">{contents}</a>'


def _commit1(project, label, log):
    commit_id, date, tz, message = log.split('|', maxsplit=3)

    if tz == '+0100':
        tz = 'CET '
    elif tz == '+0200':
        tz = 'CEST'

    date = f'{date} {tz}'
    url = f'{project.git_url}/commit/{commit_id}'

    return f'{label}: {_a(url, date)}: {message}'


def summary1(project):
    desc = project.poetry['description']
    stars = project.github_info['stargazers_count']
    star = stars > 1 and f' (🌟 {stars})' or ''
    desc_line = _a(project.git_url, desc) + star

    commits = project.git('log', *LOG_FLAGS, out=True).splitlines()
    latest_line = _commit1(project, 'Latest commit', commits[0])

    if commit := next((c for c in commits if VERSION(c)), None):
        release_line = _commit1(project, f'Latest release', commit)
    else:
        release_line = '(Unreleased)'

    lines = desc_line, release_line, latest_line
    summary = '\n<br>\n'.join(lines)
    return summary


def _commit(project, label, log):
    commit_id, date, message = (p.strip() for p in log.split('|', maxsplit=2))

    url = f'{project.git_url}/commit/{commit_id}'
    link = _a(url, date)

    return f'{label} {link} {message}'


def summary(project):
    e1, _, e2 = project.description_parts
    name = f'<code>{project.name}</code>'
    link = _a(project.git_url, name)

    try:
        stars = project.github_info['stargazers_count']
    except KeyError:
        print(project.github_info)
        raise
    star = stars > 1 and f' (🌟 {stars})' or ''
    desc_line = f'{e1} {link} {e2}' + star

    commits = project.git('log', *LOG_FLAGS, out=True).splitlines()
    latest_line = _commit(project, 'Latest', commits[0])

    if commit := next((c for c in commits if VERSION(c)), None):
        release_line = _commit(project, f'Release', commit)
    else:
        release_line = '(Unreleased)'

    lines = desc_line, release_line, latest_line
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
    print(result)


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
