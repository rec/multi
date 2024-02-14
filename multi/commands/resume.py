from .. projects import REC


def resume():
    from .. import resume

    src = REC.path / 'resume.md'
    assert src.exists()
    resume = src.with_suffix('.pdf')
    REC.run('pandoc --from=gfm --to=pdf -o resume.pdf resume.md'.split())
