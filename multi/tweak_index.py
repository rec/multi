import re
import xmod


@xmod
def tweak_index(project, path):
    e1, desc, e2 = project.description_parts
    name = project.name

    p1 = f'<p>{e1}.*?{e2}</p>'
    p2 = f'(<h2 id="{name}.{name}")'
    r2 = r'<br/> <h1 class="doc doc-heading"> API documentation </h1> \1'

    s1 = path.read_text()
    s2 = re.sub(p1, '', s1, count=1)
    s3 = re.sub(p2, r2, s2, count=1)

    d1, d2 = (s1 == s2), (s2 == s3)
    if d1 or d2:
        project.p('Unchanged', d1, d2)
        print(p1, p2)
    path.write_text(s3)


def rewrite(path):
    from lxml import etree
    from pathlib import Path

    path = Path(path)
    source = path.read_text().strip()
    html = etree.HTML(source)
    print(html, dir(html))

    target = path.parent / (path.stem + '-rewrite.html')
    out = etree.tostring(html, pretty_print=True, method='html')
    if isinstance(out, str):
        print('str')
        target.write_text(out)
    else:
        print('bytes', len(source), len(out))
        target.write_bytes(out)
