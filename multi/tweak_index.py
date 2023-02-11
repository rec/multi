from . import html_context
import re
import xmod


@xmod
def tweak_index(project, path):
    with html_context(path) as tree:
        parent, = tree.xpath('//div[@class="doc doc-contents first"]')
        child, = parent.xpath('p[1]')
        print(parent.text, child.text)
        parent.remove(child)
