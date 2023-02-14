from . import html_context
from lxml import etree
import xmod


@xmod
def tweak_index(project, path):
    with html_context(path) as tree:
        fix_title1(project, tree)
        fix_title2(project, tree)
        fix_api(tree)


def fix_title1(project, tree):
    remove(project, tree, '//div[@class="doc doc-contents first"]/p[1]')


def fix_title2(project, tree):
    remove(project, tree, f'//h1[starts-with(@id, "{project.name}-")]')


def insert_before(elem, child):
    # https://stackoverflow.com/questions/72184837
    elem.insert(0, child)
    child.tail, elem.text = elem.text, None


def remove(project, tree, xpath):
    if child := tree.xpath(xpath):
        e = child[0]
        text = (getattr(e, 'text', None) or str(e))[:128]
        project.p('Removing', text)
        e.getparent().remove(e)


def fix_api(tree):
    if child := tree.xpath('//div[@class="doc doc-children"]'):
        e = etree.Element('h1')
        e.text = 'API Documentation'
        child[0].addprevious(etree.Element('hr'))
        child[0].addprevious(etree.Element('p'))
        child[0].addprevious(e)
