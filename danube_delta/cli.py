
import os
import sys
import shutil
import importlib.util
from datetime import datetime, timedelta

import sh
import click
from slugify import slugify
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


@blog.command(help='Starts a new article')
@click.option('--open/--no-open', default=True, help='Open in editor')
@click.pass_context
def write(context, open):
    config = context.obj

    title = click.prompt('Title')
    author = click.prompt('Author', default=config.get('DEFAULT_AUTHOR'))

    slug = slugify(title)
    pub_date = datetime.now() + timedelta(hours=2)
    basename = '{:%Y-%m-%d}_{}.md'.format(pub_date, slug)

    template = 'Title: {}\nDate: {:%Y-%m-%d %H:%M:%S}\nAuthor: {}\n\n\n'
    template += 'Text...\n\n'
    template += '![image description]({{filename}}/images/your-photo.jpg)\n\n'
    template += 'Text...\n\n'
    file_content = template.format(title, pub_date, author)

    os.makedirs(config['CONTENT_DIR'], exist_ok=True)
    path = os.path.join(config['CONTENT_DIR'], basename)
    with click.open_file(path, 'w') as f:
        f.write(file_content)

    click.echo(path)
    if open:
        click.launch(path)


@blog.command(help='Opens local preview of your blog website')
@click.pass_context
def preview(context):
    config = context.obj
    state = {'ready': False}

    def open_browser(line):
        if not state['ready'] and line.startswith('Done: Processed'):
            state['ready'] = True
            click.launch('http://localhost:8000')
        return line

    server = None
    pelican = None

    os.chdir(config['OUTPUT_DIR'])
    try:
        server = sh.python(
            '-m', 'http.server', '8000',
            _bg=True,
        )
        pelican = sh.pelican(
            config['CONTENT_DIR'],
            output=config['OUTPUT_DIR'],
            settings=os.path.join(config['CWD'], config['SETTINGS_PATH']),
            autoreload=True, debug=True, ignore_cache=True,
            _bg=True, **redirect_output(open_browser)
        )
        server.wait()
        pelican.wait()

    except:
        if server is not None:
            server.process.kill()
        if pelican is not None:
            pelican.process.kill()
        raise


@blog.command(help='Looks for errors in source code of your blog')
@click.pass_context
def lint(context):
    try:
        sh.flake8('.', exclude='env', **redirect_output())
    except sh.ErrorReturnCode:
        context.exit(1)


@blog.command(help='Saves changes and sends them to GitHub')
@click.pass_context
def publish(context):
    raise NotImplementedError


@blog.command(help='Uploads new version of your public blog website')
@click.pass_context
def deploy(context):
    config = context.obj

    click.echo('Generating HTML...')
    sh.pelican(
        config['CONTENT_DIR'],
        output=config['OUTPUT_DIR'],
        settings=os.path.join(config['CWD'], config['SETTINGS_PATH']),
        _env={'PRODUCTION': '1'},
        **redirect_output()
    )

    click.echo('Removing unnecessary output...')
    unnecessary_paths = [
        'author', 'category', 'drafts', 'tag', 'feeds', 'tags.html',
        'authors.html', 'categories.html',
    ]
    for path in unnecessary_paths:
        remove_path(os.path.join(config['OUTPUT_DIR'], path))

    if os.environ.get('TRAVIS'):  # Travis CI
        click.echo('Setting up Git...')
        sh.git.config('user.name', sh.git('show', format='%cN', s=True))
        sh.git.config('user.email', sh.git('show', format='%cE', s=True))

        github_token = os.environ.get('GITHUB_TOKEN')
        repo_slug = os.environ.get('TRAVIS_REPO_SLUG')
        origin = 'https://{}@github.com/{}.git'.format(github_token, repo_slug)
        sh.git.remote('set-url', 'origin', origin)

    click.echo('Rewriting gh-pages branch...')
    commit_message = 'Published :notebook_with_decorative_cover:'
    sh.ghp_import('-m', commit_message, config['OUTPUT_DIR'])

    click.echo('Pushing to GitHub...')
    sh.git.push('origin', 'gh-pages', force=True)

    click.echo('Done!')


def load_settings_file_as_dict(filename):
    file_spec = importlib.util.spec_from_file_location('settings', filename)
    module = importlib.util.module_from_spec(file_spec)
    file_spec.loader.exec_module(module)

    config = {}
    for (key, value) in module.__dict__.items():
        if key.upper() == key:
            config[key] = value
    return config


def remove_path(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path, ignore_errors=True)


def redirect_output(filter_fn):
    def redirect_stdout(line, stdin, process):
        if filter_fn:
            line = filter_fn(line)
        sys.stdout.write(line)

    def redirect_stderr(line, stdin, process):
        if filter_fn:
            line = filter_fn(line)
        sys.stderr.write(line)

    return {'_out': redirect_stdout, '_err': redirect_stderr}
