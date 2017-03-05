import os
import importlib.util

import click
from pelican.settings import DEFAULT_CONFIG


@click.group()
@click.version_option()
@click.pass_context
def blog(context):
    cwd = os.getcwd()

    settings_path = 'settings.py'
    settings_file = os.path.join(cwd, settings_path)

    config = {'CWD': cwd, 'SETTINGS_PATH': settings_path}
    config.update(DEFAULT_CONFIG)
    config.update(load_settings_file_as_dict(settings_file))

    config['CONTENT_DIR'] = os.path.join(cwd, config['PATH'])
    config['OUTPUT_DIR'] = os.path.join(cwd, config['OUTPUT_PATH'])

    context.obj = config


from . import (  # NOQA
    update,
    write,
    photos,
    preview,
    publish,
    lint,
    deploy,
)


def load_settings_file_as_dict(filename):
    file_spec = importlib.util.spec_from_file_location('settings', filename)
    module = importlib.util.module_from_spec(file_spec)
    file_spec.loader.exec_module(module)

    config = {}
    for (key, value) in module.__dict__.items():
        if key.upper() == key:
            config[key] = value
    return config
