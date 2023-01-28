from projects import over_projects
import editor


@over_projects
def edit_all(p, path):
    editor(p / path)


if __name__ == '__main__':
    import sys

    path, = sys.argv[1:]
    # edit_all(path)
    print(path)
