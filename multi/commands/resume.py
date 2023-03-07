from .. projects import REC


def resume():
    from .. import resume

    src = REC.path / 'resume.md'
    assert src.exists()
    text = src.read_text()
    prefix = src.parent / src.stem
    html = resume.make_html(text, prefix=str(prefix))
    html_file = prefix.with_suffix('.html')
    html_file.write_text(html)
    resume.write_pdf(html, prefix=str(prefix))
    html_file.unlink()
