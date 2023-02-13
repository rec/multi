from . import html_context
import re
import xmod


@xmod
def tweak_index(project, path):
    with html_context(path) as tree:
        if abbrev := tree.xpath('//div[@class="doc doc-contents first"]'):
            parent = abbrev[0]
            if children := parent.xpath('p[1]'):
                child = children[0]
                print('Removing', child.text)
                parent.remove(child)
