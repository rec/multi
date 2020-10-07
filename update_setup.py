from projects import over_projects
import re
import safer
import yaml

LANGUAGE = re.compile(r"'Programming Language :: Python :: (\d\.\d)'")
TRAVIS = re.compile(r'- python: (\d\.\d)-dev')
DRY_RUN = True

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

    if False:
        print(filename, ': Added 3.9' if success else 'No change')


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


@over_projects
def update(p):
    update_setup(p)
    update_travis(p)


if __name__ == '__main__':
    update()
