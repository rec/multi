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
