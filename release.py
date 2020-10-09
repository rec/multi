from projects import over_projects
import subprocess
import webbrowser


@over_projects
def release(p, start=''):
    if p.name < start:
        return

    answer = input(f'{p}: (yN)? ').lower().strip() or 'y'
    if not answer.startswith('y'):
        return

    changelog = ''.join(list((p / 'CHANGELOG').open())[:20])
    subprocess.run('pbcopy', universal_newlines=True, input=changelog)
    webbrowser.open(f'https://github.com/rec/{p.name}/releases/new')
