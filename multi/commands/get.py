import subprocess


def get(project, address, *args):
    data = _getattrs(project, [address])

    if not callable(data):
        project.p(data)
        return

    try:
        result = data(*args)
    except Exception as e:
        result = e

    if not isinstance(result, (type(None), subprocess.CompletedProcess)):
        project.p(result)
    print()


def _getattr(data, a):
    for part in a and a.split('.'):
        try:
            data = data[part]
        except Exception:
            try:
                data = getattr(data, part)
            except AttributeError:
                return
    yield data


def _getattrs(data, argv):
    result = {a: d for a in argv or [''] for d in _getattr(data, a)}

    if len(result) == 1 and len(argv) == 1:
        return result.popitem()[1]
    return result
