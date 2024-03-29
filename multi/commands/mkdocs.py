from . import readme
from .. import configs, tweak_index
from .. paths import MKDOCS, MKDOCS_BINARY
import shutil
import threading
import time


def fix(project):
    if not project.has_gh_pages():
        project.p('no gh-pages')
    else:
        mkd = project.gh_pages / 'assets/_mkdocstrings.css'
        if mkd.exists():
            project.p('exists')
        elif not mkd.parent.exists():
            project.p('no parent')
        elif False:
            shutil.copyfile('/code/safer/site/assets/_mkdocstrings.css', mkd)
            project.git('add', mkd, cwd=project.gh_pages)
            project.commit('Add _mkdocstrings.css', mkd, cwd=project.gh_pages)
        else:
            print('Missing', mkd)


def mkdocs(project):
    mkdocs_build(project)
    copy_and_edit_site(project)
    readme.write_readme(project)


def is_mkdocs(project):
    return (
        project.is_singleton
        and (project.path / 'docs').exists()
        and 'working' in project.tags
    )


def open_all(project):
    project.open_doc()
    project.open_gh()
    project.open_git()


def mkdocs_build(project):
    docs = sorted(i for i in MKDOCS.rglob('*') if not i.name.startswith('.'))
    written = [f for d in docs for f in _write_doc(project, d)]
    project.run(MKDOCS_BINARY, 'build')
    if configs.push:
        msg = 'Update mkdocs documentation with rec/multi 0.1.1'
        project.git.commit(msg, *written)


_PROCESS = {
    'index.html': tweak_index,
}


def copy_and_edit_site(project):
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

            target.parent.mkdir(exist_ok=True, parents=True)
            shutil.copyfile(src, target)
            if process := _PROCESS.get(str(rel)):
                process(project, target)

            if src.read_bytes() != old_target:
                results.append(target)

    if not results:
        project.p('no results')
        return

    project.p(*results)
    if configs.push:
        push_site_changes(project)

    if configs.open:
        if configs.push:
            project.open_doc()
        else:
            project.open_gh()


def push_site_changes(project):
    lines = project.git(
        'status', '--porcelain', out=True, cwd=project.gh_pages
    )
    if all(i.endswith('.gz') for i in lines):
        return

    project.git('add', '.', cwd=project.gh_pages)

    project.p()
    commit_id = project.commit_id()[:7]

    msg = f'Deployed {commit_id} with rec/multi version 0.1.1'
    project.git.commit(msg, cwd=project.gh_pages)


def _accept(project, doc):
    if not doc.exists():
        return True
    if doc.is_dir():
        return False
    return not (doc.name == 'index.md' and 'custom_index' in project.tags)


def _write_doc(project, doc):
    if not _accept(project, doc):
        return

    contents = doc.read_text()
    if '.tpl' in doc.suffixes:
        contents = contents.format(project=project)

        suffixes = ''.join(s for s in doc.suffixes if s != '.tpl')
        while doc.suffix:
            doc = doc.with_suffix('')
        doc = doc.with_suffix(suffixes)

    p = project.path / doc.relative_to(MKDOCS)
    p.parent.mkdir(exist_ok=True)
    c2 = p.exists() and p.read_text()
    if c2 != contents:
        p.write_text(contents)
        yield p


def serve(project, *args):
    if project.is_singleton:
        args = '-w', project.name + '.py', *args

    args = MKDOCS_BINARY, 'serve', f'--dev-addr={project.server_url}', *args
    threading.Thread(target=project.run, args=args, daemon=True).start()

    time.sleep(0.5)
    project.open_server()
    return True
