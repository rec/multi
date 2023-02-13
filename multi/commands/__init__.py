import sys


def name(project):
    print(project.site_name)


def _exit(*args):
    # Elsewhere.
    if args:
        print(*args, file=sys.stderr)
        exit(-1)
    exit(0)
