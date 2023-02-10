from lxml import etree
from pathlib import Path
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


def rewrite(path='/code/abbrev/.cache/gh-pages/index.html'):
    from bs4 import BeautifulSoup

    path = Path(path)
    source = path.read_text().strip()
    soup = BeautifulSoup(source, 'html.parser')
    return soup


from lxml import etree


def run(s):
    html = etree.HTML(s)
    assert html is not None, 'etree.HTML(s) returned None!'

    return etree.tostring(html, pretty_print=True, method="html").decode()


def round_trip(s):
    print('Result:')
    print(run(s))


def old_compare_both():
    p1 = '<html><head><title>ANT</title></head><body></body></html>'

    # Works
    round_trip(p1)
    round_trip('\n' + p1)

    p2 = """<html><head><title>🐜</title></head><body>
휀휁휂휃휄휅휆휇휈😆</body></html>"""

    # Works
    round_trip(p2.encode())
    round_trip(('\n' + p2).encode())

    # Fails
    round_trip(p2)         # Wrong answer
    round_trip('\n' + p2)  # Returns None


def compare_both():
    cps = (
        0x10000,
        0x10001,
        0x10002,
        0x10003,

        0x10010,
        0x10020,
        0x10030,
        0x100FF,

        0x10100,
        0x10200,
        0x10300,

        0x11000,
        0x12000,
        0x13000,

        0x20000,
        0x30000,
        0x40000,
        0x80000,
        0x100000,
        0x100001,
    )
    cps = range(0x010000, 0x010100)

    cps = range(0x80, 0x014000)

    def cpt(cp):
        try:
            c = chr(cp)
            c.encode()
        except UnicodeEncodeError:
            return ''
        return f'0x{cp:06x}: {c}\n'

    s = ''.join(cpt(cp) for cp in cps)

    p1 = f'<html><head><title>test</title></head><body>\n{s}\n</body></html>'

    s = run(p1.encode())

    import re

    pat = re.compile(r'0x(.*?): ' + r'(?:&#(\d\d\d);){1,4}\n')

    diff = -1

    def rep(m):
        if True:
            return m.group(0)
        nonlocal diff

        n, *parts = m.groups()
        h = ''.join(hex(int(i))[2:] for i in parts)
        before, after = int(n, 16), int(h, 16)
        d2 = before - after
        if d2 == diff:
            return ''
        diff = d2
        return f'0x{n}: 0x{diff:x}\n'

    print(pat.sub(rep, s))

def rewrite2(path=Path('test-index.html')):
    broken_html = "<html><head><title>test<body><h1>page title</h3>"
    print(round_trip(broken_html))

    source = path.read_text().strip()
    print(round_trip(source))


def rewrite_lxml(path):
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


if __name__ == '__main__':
    compare_both()
