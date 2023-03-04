from .. import configs, project, projects

BLOG = project.Project('rec.github.io')


def publish():
    projects.MULTI.run('pelican', cwd=BLOG.path)
    if BLOG.git.is_dirty() and configs.push:
        BLOG.git('add', '.')
        BLOG.git('commit', '-m', 'Automatically updated by rec/multi')
        BLOG.git('push')
