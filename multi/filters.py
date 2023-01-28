def is_poetry(project):
    p = project.pyproject
    return p.exists() and 'tool.poetry' in tomli.loads(p.read_text())
