import re
import xmod


@xmod
def tweak_index(project, path):
    e1, desc, e2 = project.description_parts
    name = project.name

    s1 = path.read_text()
    s2 = re.sub(f'<p>{e1}.*?{e2}</p>', '', s1, count=1)
    s3 = re.sub(
        f'(<h2 id="{name}.{name}")',
        r'<br/> <h1 class="doc doc-heading"> API documentation </h1> \1',
        s2,
        count=1)

    d1, d2 = (s1 == s2), (s2 == s3)
    if d1 or d2:
        project.p('Unchanged', d1, d2)
    path.write_text(s3)
