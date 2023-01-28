def _pyproject(path):
    return path / 'pyproject.toml'


def is_poetry(project, settings, path):
    p = _pyproject(path)
    return p.exists() and 'tool.poetry' in tomli.loads(p.read_text())
