
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

    BLOG_CONFIG = load_settings_file_as_dict(os.path.join(cwd, settings_path))

    config = {'CWD': cwd, 'SETTINGS_PATH': settings_path}
    config.update(DEFAULT_CONFIG)
    config.update(BLOG_CONFIG)

    context.obj = config


@blog.command(help='Runs development server')
@click.pass_context
def develop(context):
    config = context.obj

    click.echo('Generating HTML...')
    build(config, autoreload=True)


@blog.command(help='Looks for errors in source code of your blog')
@click.pass_context
def lint(context):
    try:
        sh.flake8('.', exclude='env', **redirect_output)
    except sh.ErrorReturnCode:
        context.exit(1)


@blog.command(help='Generates HTML and pushes your new gh-pages to GitHub')
@click.pass_context
def deploy(context):
    config = context.obj
    output_dir = os.path.join(config['CWD'], config['OUTPUT_PATH'])

    click.echo('Generating HTML...')
    build(config, production=True)

    click.echo('Removing unnecessary output...')
    unnecessary_paths = [
        'author', 'category', 'drafts', 'tag', 'feeds', 'tags.html',
        'authors.html', 'categories.html',
    ]
    for path in unnecessary_paths:
        remove_path(os.path.join(output_dir, path))

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
    sh.ghp_import('-m', commit_message, output_dir)

    click.echo('Pushing to GitHub...')
    sh.git.push('origin', 'gh-pages', force=True)

    click.echo('Done!')


@blog.command(help='Creates new article and opens it in your editor')
@click.option('--open/--no-open', default=True, help='Open in editor')
@click.pass_context
def article(context, open):
    config = context.obj
    content_dir = os.path.join(config['CWD'], config['PATH'])

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

    os.makedirs(content_dir, exist_ok=True)
    path = os.path.join(content_dir, basename)
    with click.open_file(path, 'w') as f:
        f.write(file_content)

    click.echo(path)
    if open:
        click.launch(path)


def load_settings_file_as_dict(filename):
    file_spec = importlib.util.spec_from_file_location('settings', filename)
    module = importlib.util.module_from_spec(file_spec)
    file_spec.loader.exec_module(module)

    config = {}
    for (key, value) in module.__dict__.items():
        if key.upper() == key:
            config[key] = value
    return config


def build(config, production=False, autoreload=False):
    options = redirect_output.copy()
    options['autoreload'] = autoreload

    if production:
        options['_env'] = {'PRODUCTION': True}
    else:
        options['debug'] = True
        options['ignore_cache'] = True

    sh.pelican(
        os.path.join(config['CWD'], config['PATH']),
        output=os.path.join(config['CWD'], config['OUTPUT_PATH']),
        settings=os.path.join(config['CWD'], config['SETTINGS_PATH']),
        **options
    )


def remove_path(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path, ignore_errors=True)


def redirect_stdout(line, stdin, process):
    sys.stdout.write(line)


def redirect_stderr(line, stdin, process):
    sys.stderr.write(line)


redirect_output = {'_out': redirect_stdout, '_err': redirect_stderr}
