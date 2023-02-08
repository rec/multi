import subprocess


def get(project, address):
    if (result := get_or_call(project, address)) is not None:
        project.p(result)


def get_or_call(project, address):
    i = 0
    if not (data := _getattr(project, address)):
        return

    data, = data
    if call := callable(data):
        try:
            data = data(*args)
        except Exception as e:
            return e

    if isinstance(data, subprocess.CompletedProcess):
        return data.returncode or None

    if isinstance(data, list):
        # tomlkits arrays don't print
        return list(data)

    return data


def _getattr(data, a):
    for part in (a and a.split('.')):
        try:
            data = data[part]
        except Exception:
            try:
                data = getattr(data, part)
            except AttributeError:
                return
    return [data]
