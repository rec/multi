def is_poetry(project):
    import json
    import tomlkit

    if (p := project.pyproject).exists():
        t = tomlkit.loads(p.read_text())
        return t.get('tool', {}).get('poetry', {})
