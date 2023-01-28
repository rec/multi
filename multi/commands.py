import json


def name(project, settings, path):
    print(project)


def show(project, settings, path):
    print(json.dumps(locals(), default=str, indent=4))
