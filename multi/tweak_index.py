import re
import xmod



@xmod
def tweak_index(project, path):
    e1, desc, e2 = project.description_parts

    s = path.read_text()
    s = re.sub(f'<p>{e1}.*{e2}</p>', '', s, count=1)
    path.write_text(s)
