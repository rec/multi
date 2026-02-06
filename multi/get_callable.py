import importlib
from functools import wraps


def get_callable(name):
    def get_one_callable(path):
        module = importlib.import_module(path)
        none = object()

        if callable(f := getattr(module, attr, none)):
            return f
        if f is none:
            msg = ValueError(f'ERROR: {name} does not exist ({module=}, {f=})')
        else:
            msg = f'ERROR: {name} is not callable ({module=}, {f=})'
        raise ValueError(msg)

    path, _, attr = name.rpartition('.')

    try:
        return get_one_callable(path)
    except ValueError as e:
        try:
            return get_one_callable(f'{path}.{attr}')
        except ValueError as f:
            f.args = f.args + e.args
            raise
        except ModuleNotFoundError as f:
            raise ValueError(*e.args, *f.args) from None


def make_filter(filter_desc):
    name, *args = filter_desc.split(':')
    f = get_callable('multi.filters.' + (name or DEFAULT_FILTER))

    @wraps(f)
    def filter(project):
        return bool(f(project, *args))

    return filter


DEFAULT_FILTER = 'prop'
