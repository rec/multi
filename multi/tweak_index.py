from lxml import etree, html
import xmod


@xmod
def tweak_index(project, text):
    tree = html.fromstring(text)
    root = tree.getroot()
    result = etree.tostring(root)

    return result
