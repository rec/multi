from . import html_context
import xmod


@xmod
def tweak_index(project, path):
    with html_context(path) as tree:
        fix_title(tree)
        fix_api(tree)


def fix_title(tree):
    if abbrev := tree.xpath('//div[@class="doc doc-contents first"]'):
        parent = abbrev[0]
        if children := parent.xpath('p[1]'):
            child = children[0]
            print('Removing', child.text)
            parent.remove(child)


def insert_before(elem, child):
    # https://stackoverflow.com/questions/72184837
    elem.insert(0, child)
    child.tail, elem.text = elem.text, None


def fix_api(tree):
    ...
