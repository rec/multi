from .. import projects
from .. project import Project
import re
import time

CATEGORIES = (
    'production-ready',
    'beta',
    'experimental',
    'personal',
    'mothballed',
)
REC = Project('rec', len(projects.PROJECTS))
LOG_FLAGS = '--pretty=format:%h|%cd|%s', '--date=format:%g/%m/%d'
README = 'README.md'
TIME_FORMAT = '%y/%m/%d, %H:%M:%S'

"""
Per project data:

description (🌟 # if # > 1)
Release v1.0.2:  [date] [message]
Latest commit:  [date] [message]

"""
MSG = f'Automatically update {README}'


def dashboard():
    resume()
    readme()


def resume():
    from .. import resume

    src = REC.path / 'resume.md'
    assert src.exists()
    text = src.read_text()
    prefix = src.parent / src.stem
    html = resume.make_html(text, prefix=str(prefix))
    html_file = prefix.with_suffix('.html')
    html_file.write_text(html)
    resume.write_pdf(html, prefix=str(prefix))
    html_file.unlink()


def readme():
    _write_contents()
    if REC.git.is_dirty():
        _commit_readme()
    else:
        print('No change')


def _write_contents():
    readme = REC.path / README
    text, _ = readme.read_text().split(SPLIT)

    tables = (make_table(k, v) for k, v in _categories().items())
    tables = '\n<p>\n'.join(tables)
    timestamp = time.strftime('%Y/%m/%d, %H:%M:%S')
    program = 'https://github.com/rec/multi'
    rendered = f'Rendered at {timestamp} by {program}'
    readme.write_text(f'{text}{SPLIT}{tables}\n\n{rendered}')


def _commit_readme():
    line, = REC.git.commits('-1')
    if line.strip().endswith(MSG):
        print('Amending')
        REC.git('commit', '--amend', README, '--no-edit')
        REC.git('push', '-f')
    else:
        print('Committing')
        REC.git.commit(MSG, README)


def _categories():
    categories = {c: [] for c in CATEGORIES}
    tags = projects.DATA['tags']
    for p in projects.PROJECTS.values():
        for c in CATEGORIES:
            if p.name in tags[c]:
                categories[c].append(p)

    return categories


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

    commits = project.git.commits()
    latest_line = _commit(project, '🕰', commits[0])

    if commit := next((c for c in commits if VERSION(c)), None):
        release_line = _commit(project, '🟢', commit)
    else:
        release_line = ''

    lines = desc_line, desc_line2, release_line, latest_line
    summary = '\n<br>\n'.join(lines)
    return summary


def _cell(project):
    cell = summary(project)
    return f'<td>{cell}</td>\n'


def _row(projects):
    cells = '\n'.join(_cell(p) for p in projects)
    return f'<tr>{cells}</tr>'


def make_table(name, projects):
    pairs = (projects[i: i + 2] for i in range(0, len(projects), 2))
    body = '\n'.join(_row(p) for p in pairs)

    label = f'<h2>{name.capitalize()}</h2>\n'
    return f'{label}<table><tbody>{body}</tbody></table>'


VERSION = re.compile(r'ersion v\d+\.\d+\.\d+$').search
SPLIT = '<!--- Automatically generated content below -->'
