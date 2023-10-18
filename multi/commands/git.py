import string
from .. projects import DATA, PROJECTS, REC
import time


def recent_commits():
    it = ((k, v.git.commits('-1', long=True)[0]) for k, v in PROJECTS.items())
    it = ((k, v.split('|')) for k, v in it)
    commits = sorted(it, key=lambda x: x[1][1])
    print('commits', *commits, sep='\n')


def commit(project, *args):
    if project.name != 'multi' and project.git.is_dirty():
        project.git('commit', '-am', ' '.join(args))


def state(project):
    project.p(f'{project.git.is_dirty() * "*":1} {project.branch()}')


def fix_gitignore(project):
    gi = project.path / '.gitignore'
    lines = gi.read_text().splitlines()
    if 'site/' in lines:
        return
    if matches := [i for i, line in enumerate(lines) if line == '/site']:
        for i in matches:
            lines[i] = 'site/'
        msg = 'Replaced /site with site/ in .gitignore'
    else:
        lines.append('site/')
        msg = 'Added site/ to .gitignore'

    gi.write_text('\n'.join(lines) + '\n')
    project.git.commit(msg, gi)
    project.p(gi, '/site -> site/')


def tweak_github(project):
    project.run.gh(
        'repo',
        'edit',
        '--enable-merge-commit=false',
        '--enable-rebase-merge',
        '--enable-squash-merge=false',
    )
    project.p()


def pull_rename(project):
    if project.branch() == 'rst-to-md':
        project.git('switch', 'main')

        project.git('merge', 'rst-to-md')
        project.git('push')

        project.git('delete', 'rst-to-md')


def remove_data(project):
    commits = project.git('log', '--oneline', out=True)
    matches = 'multi.tag', 'mult.tag'
    ic = enumerate(commits)

    remove = [i for i, c in ic if any(m in c for m in matches)]

    if True:
        print(f'cd {project.path} && git rebase -i HEAD~30')
        print()
        return

    project.p('git', 'rebase', f'~{remove[-1] + 3}')
    print(*(commits[i] for i in remove), sep='\n')
    print()

    chars = string.ascii_lowercase[:remove[-1] + 2]
    remain = [c for i, c in enumerate(chars) if i not in remove]
    res = ''.join(remain)
    assert res

    # project.p(f'{str(remove):15} {res}')

    # print(f'cd {project.path} && git permute {res}')
    # project.git('push', '--force-with-lease')
