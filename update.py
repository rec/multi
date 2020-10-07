from projects import over_projects
import re
import safer
import versy
import yaml
import subprocess
import webbrowser


LANGUAGE = re.compile(r"'Programming Language :: Python :: (\d\.\d)'")
TRAVIS = re.compile(r'- python: (\d\.\d)-dev')
DRY_RUN = not True

def run(*cmd):
    print('$', *cmd)
    if not DRY_RUN:
        if (code := subprocess.run(cmd).returncode):
            raise ValueError('Ooops', str(code))


def update_setup(p, new_version='3.9'):
    filename = p / 'setup.py'
    success = False
    version = None

    with safer.writer(filename, dry_run=DRY_RUN) as fp:
        for line in open(filename):
            if (match := LANGUAGE.search(line)):
                version = match.group(1)
                last_line = line
            elif version and version < new_version:
                # Won't work for 3.10! :-)
                fp.write(last_line.replace(version, new_version))
                version = None
                success = True
            fp.write(line)

    print(filename, ': Added 3.9' if success else 'No change')
    return filename


def update_travis(p, new_version='3.9'):
    filename = p / '.travis.yml'

    travis = yaml.safe_load(open(filename))
    include = travis.setdefault('matrix', {}).setdefault('include', [])
    versions = [str(i.get('python', '')) for i in include] or ['']
    version = max(versions)
    if version < new_version:
        include.append({'python': '3.8-dev', 'dist': 'xenial'})
        with safer.writer(filename, dry_run=DRY_RUN) as fp:
            yaml.safe_dump(travis, fp, indent=2)
        print(filename, 'rewritten')
    else:
        print(filename, 'no change')

    return filename


def commit(p, *files, new_version='3.9'):
    run('git', 'commit', '-m', f'Enable Python {new_version}', *files)
    run('git', 'push')
    if not DRY_RUN:
        versy(action='patch', push=True)
    webbrowser.open(f'https://github.com/rec/{p.name}/commits/master')


@over_projects
def update(p):
    if False:
        commit(p, update_setup(p), update_travis(p))
    else:
        run('git', 'restore', '.')


if __name__ == '__main__':
    update()
