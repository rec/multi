from . import html_context
from lxml import etree
import xmod


@xmod
def tweak_index(project, path):
    with html_context(path) as tree:
        fix_title1(project, tree)
        fix_title2(project, tree)
        add_api_documentation(project, tree)
        remove_extra_link(project, tree)


def fix_title1(project, tree):
    remove(project, tree, '//div[@class="doc doc-contents first"]/p[1]')


def fix_title2(project, tree):
    remove(project, tree, f'//h1[starts-with(@id, "{project.name}-")]')


def remove_extra_link(project, tree):
    remove(project, tree, '//a[@class="md-nav__link md-nav__link--active"]')


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


def add_api_documentation(project, tree):
    if not project.get_value('api_documentation', True):
        return

    doc_children = tree.xpath('//div[@class="doc doc-children"]')
    if not doc_children:
        print('Did not add doc_children')
        return

    if False:
        nav_list = tree.xpath('//ul[@class="md-nav__list"]')

        assert nav_list
        print(len(nav_list))
        print(dir(nav_list))
        print(*(dict(i.items()) for i in nav_list), sep='\n')

        item = nav_list[0]
        print(len(item))
        print(item[0].items(), item[0].text)

    e = etree.Element('h1', id=project.api_anchor)
    e.text = 'API Documentation'
    child = doc_children[0]
    child.addprevious(etree.Element('hr'))
    child.addprevious(etree.Element('p'))
    child.addprevious(e)
