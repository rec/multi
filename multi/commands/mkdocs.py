from .. import configs, tweak_index
from .. paths import MKDOCS, MKDOCS_BINARY
import shutil
import threading
import time


def mkdocs(project):
    if is_mkdocs(project):
        build(project)
        process(project)
        if configs.open:
            project.open_gh()


def is_mkdocs(project):
    return (
        project.is_singleton
        and (project.path / 'docs').exists()
        and 'working' in project.tags
    )


def build(project):
    if not is_mkdocs(project):
        return

    docs = sorted(i for i in MKDOCS.rglob('*') if not i.name.startswith('.'))
    written = [f for d in docs for f in _write_doc(project, d)]
    project.run(MKDOCS_BINARY, 'build')
    if configs.push:
        msg = 'Update mkdocs documentation with rec/multi 0.1.1'
        project.git.commit(msg, *written)


_PROCESS = {
    'index.html': tweak_index,
}


def process(project):
    site = project.path / 'site'
    if not site.exists():
        return

    results = []
    for src in sorted(site.rglob('*')):
        if not (src.name.startswith('.') or src.is_dir()):
            rel = str(src.relative_to(site))
            target = project.gh_pages / rel

            old_target = target.exists() and target.read_bytes()

            if configs.verbose:
                print('shutil.copyfile', src, target)
            shutil.copyfile(src, target)
            if process := _PROCESS.get(target.name):
                process(project, target)

            if src.read_bytes() != old_target:
                results.append(target)

    if not results:
        return

    project.p(*results)
    if configs.push:
        push(project)

    if configs.open:
        if configs.push:
            project.open_doc()
        else:
            project.open_gh()


def push(project):
    if project.git.is_dirty(cwd=project.gh_pages):
        project.p()
        commit_id = project.commit_id()[:7]

        msg = f'Deployed {commit_id} with rec/multi version 0.1.1'
        project.git.commit(msg, cwd=project.gh_pages)


def _write_doc(project, doc):
    if doc.is_dir():
        return

    contents = doc.read_text()
    if '.tpl' in doc.suffixes:
        contents = contents.format(project=project)

        suffixes = ''.join(s for s in doc.suffixes if s != '.tpl')
        while doc.suffix:
            doc = doc.with_suffix('')
        doc = doc.with_suffix(suffixes)


    rel = project.path / doc.relative_to(MKDOCS)
    rel.parent.mkdir(exist_ok=True)
    c2 = rel.exists() and rel.read_text()
    if c2 != contents and not (rel.exists() and rel.name == 'index.md'):
        rel.write_text(contents)
        yield rel


def serve(project, *args):
    if project.is_singleton:
        args = '-w', project.name + '.py', *args

    args = MKDOCS_BINARY, 'serve', f'--dev-addr={project.server_url}', *args
    threading.Thread(target=project.run, args=args, daemon=True).start()

    time.sleep(0.5)
    project.open_server()
    return True
