from lxml import etree
from pathlib import Path
import re
import xmod
from lxml import etree


def run(s: str):
    if isinstance(s, str):
        s = s.encode()
    html = etree.HTML(s)
    t = etree.tostring(html, pretty_print=True, method="html")
    return fix_non_ascii(t.decode())


def fix_non_ascii(s):
    # Example: &#237;&#156;&#132;&#237;&#156;&#136;&#240;&#159;&#152;&#134;

    def replace(m):
        parts = [int(i.strip(';')) for i in m.group(0).split('&#') if i]
        return ''.join(to_chars(parts))

    pat = r'(&#[12]\d\d;)+'
    return re.sub(pat, replace, s)


def to_chars(parts):
    parts = parts[::-1]  # So we can pop from the end!
    while parts:
        a, b = parts.pop(), parts.pop()
        if a < 0xE0:
            yield chr(b + 0x40 * (a - 0xC2))

        elif a < 0xF0:
            c = parts.pop()
            yield chr(
                0x800 + (c - 0x80) +
                + 0x40 * (
                    (b - 0xA0)
                    + 0x40 * (a - 0xE0)
                )
            )
        else:
            c, d = parts.pop(), parts.pop()

            yield chr(
                0x010000 + (d - 0x80)
                + 0x40 * ((c - 0x80)
                    + 0x40 * ((b - 0x90)
                        + 0x40 * (a - 0xF0)
                    )
                )
            )


def attempt():
    t = '<html><head><title>🐜</title></head><body>휄휈😆</body></html>'
    print(run(t))


def compare_both():
    cps = range(0x80, 0x110000)
    # cps = range(0x80, 0x82)
    # cps = range(0x7F0, 0x1000)

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

    pat = re.compile(r'0x(.*?): ' + r'((?:&#[12]\d\d;){1,4})')

    print(pat.sub(replace1, s))


def replace1(m):
    n, parts = m.groups()
    parts = parts.strip(';').split(';')
    parts = [int(i[2:]) for i in parts]
    i = ' '.join(str(p) for p in parts)
    h = ' '.join(hex(p)[2:] for p in parts)
    gp = guess(parts)
    assert gp == int(n, 16), f'{gp} {int(n)}'
    m2 = list(PAT.search(m.group(0)).groups())
    while not m2[0]:
        m2.pop(0)
    return f'0x{n}: {h}: {i}: {" ".join(m2)}'


def replace2(m):
    parts = [int(i) for i in m.groups() if i]
    a, b, *rest = parts
    if not rest:
        assert 0xC2 <= a < 0xE0
        return chr(b + 0x40 * (a - 0xC2))

    c, *rest = rest
    if not rest:
        assert 0xE0 <= a < 0xF0
        return chr(0x800
            + (c - 0x80) +
            + 0x40 * ((b - 0xA0)
                + 0x40 * (a - 0xE0)
            )
        )

    d, = rest
    assert 0xF0 <= a, f'{a=:x}, {b=:x}, {c=:x}, {d=:x}'
    return chr(0x010000
        + (d - 0x80) +
        0x40 * ((c - 0x80) +
            0x40 * ((b - 0x90)
                + 0x40 * (a - 0xF0)
            )
        )
    )


def guess(parts):
    a, b, *rest = parts
    if not rest:
        assert 0xC2 <= a < 0xE0
        return b + 0x40 * (a - 0xC2)

    c, *rest = rest
    if not rest:
        assert 0xE0 <= a < 0xF0
        return (0x800
            + (c - 0x80) +
            + 0x40 * ((b - 0xA0)
                + 0x40 * (a - 0xE0)
            )
        )

    assert 0xF0 <= a
    d, = rest
    return (0x010000
        + (d - 0x80) +
        0x40 * ((c - 0x80) +
            0x40 * ((b - 0x90)
                + 0x40 * (a - 0xF0)
            )
        )
    )


if __name__ == '__main__':
    # compare_both()
    attempt()
