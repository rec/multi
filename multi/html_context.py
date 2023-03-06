from contextlib import contextmanager
from lxml import etree
from pathlib import Path
import xmod
import re

DIGITS = re.compile(br'&#([12]\d\d);')


@xmod
@contextmanager
def context(filename: Path):
    contents = filename.read_bytes()
    html = etree.HTML(contents)
    yield html

    t = etree.tostring(html, pretty_print=True, method="html")
    fixed = fix(t)
    filename.write_bytes(fixed)


def fix(t: bytes):
    if isinstance(t, str):
        t = t.encode()

    def replace(m):
        return bytes([int(m.group(1))])

    return DIGITS.sub(replace, t)
