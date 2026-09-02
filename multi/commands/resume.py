from ..projects import REC


def resume():
    from .shared import resume

    base = REC.path / 'resume.md'
    for lang in ('.en', '.fr'):
        src = base.with_suffix(f'{lang}.md')
        target = base.with_suffix(f'{lang}.pdf')
        assert src.exists(), src
        REC.run(f'pandoc --from=gfm --to=pdf -o {target} {src}'.split())
