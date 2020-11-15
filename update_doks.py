import editor
import info
import subprocess

PYPROJECT = 'pyproject.toml'
MESSAGE = 'Add doks settings to ' + PYPROJECT

def update_doks(p):
     has_doks = (f := p / 'README.rst').exists() and 'doks' in f.read_text()
     version = info.top_version_if_any() or info.local_version(p)
     star = 'd' if has_doks else ' '
     bang = '!' if version and version[0] >= '1' else ' '
     if bang == '!':
         if True:
             return
         print(bang, p.name, version)
     print(bang + star, p.name, version)
     if True:
         return
     editor(filename=PYPROJECT)

     subprocess.run(('git', 'commit', PYPROJECT, '-m', MESSAGE))
     subprocess.run(('git', 'push'))
