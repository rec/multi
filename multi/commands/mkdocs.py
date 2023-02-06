from .. paths import MKDOCS, MKDOCS_BINARY


def add_mkdocs(project, *argv):
    if (project.path / 'doc').exists():
        return
    docs = sorted(i for i in MKDOCS.rglob('*') if not i.name.startswith('.'))

    written = [f for d in docs for f in _write_doc(project, d)]
    assert written
    project.run(MKDOCS_BINARY, 'build')
    msg = 'Add mkdocs documentation'
    project.git.commit(msg, *written)


def _write_doc(project, doc):
    if doc.is_dir():
        return

    contents = doc.read_text()
    if '.tpl' in doc.suffixes:
        contents = contents.format(project=project)

        suffixes = ''.join(s for s in doc.suffixes if s != '.tpl')
        while doc.suffix:
            doc = doc.with_suffix('')
        doc = doc.with_suffix(suffixes)

    rel = project.path / doc.relative_to(MKDOCS)
    rel.parent.mkdir(exist_ok=True)
    rel.write_text(contents)
    yield rel
