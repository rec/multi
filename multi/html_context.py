from contextlib import contextmanager
from lxml import etree
from pathlib import Path
import xmod
import re

DIGITS = re.compile(br'(&#[12]\d\d;)+')


@xmod
@contextmanager
def context(filename: Path):
    contents = filename.read_bytes()
    html = etree.HTML(contents)
    yield html

    t = etree.tostring(html, pretty_print=True, method="html")
    filename.write_bytes(fix(t))


def fix(t: bytes):
    if isinstance(t, str):
        t = t.encode()
    return DIGITS.sub(replace, t)


def replace(m):
    parts = [int(i.strip(';')) for i in m.group(0).split('&#') if i]
    return ''.join(to_chars(parts))


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
                    + 0x40 * (a - 0xE0)))
        else:
            c, d = parts.pop(), parts.pop()

            yield chr(
                0x010000 + (d - 0x80)
                + 0x40 * ((c - 0x80)
                    + 0x40 * ((b - 0x90)     # noqa: E128
                        + 0x40 * (a - 0xF0))))  # noqa: E128
