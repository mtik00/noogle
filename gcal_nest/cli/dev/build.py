import os
import click
from jinja2 import Environment, StrictUndefined, FileSystemLoader
import ruamel.yaml


@click.command()
def build():
    """
    Build the utility
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    conf_dir = os.path.abspath(os.path.join(base_dir, 'conf'))
    instance_dir = os.path.abspath(os.path.join(base_dir, 'instance'))
    outdir = os.path.join(base_dir, '_build')

    site_config_file = os.path.join(instance_dir, 'site.yaml')
    if not os.path.exists(site_config_file):
        click.echo('ERROR: Could not find %s' % site_config_file)
        click.echo('...a sample is located in `conf`')
        click.echo('...copy `conf/site.yaml` to your instance folder, and modify it as needed')
        click.echo('...we think your instance folder is here: ' + instance_dir)
        raise click.Abort()

    return
    options = ruamel.yaml.safe_load(open(site_config_file).read())

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    env = Environment(
        loader=FileSystemLoader(conf_dir),
        undefined=StrictUndefined)

    ###########################################################################
    click.echo('Creating `_build/gcal-nest-systemd.service')
    template = env.get_template('gcal-nest-systemd.service.j2')
    content = template.render(**options)
    with open(os.path.join(outdir, 'gcal-nest-systemd.service'), 'wb') as fh:
        fh.write(content)
    click.echo('...done')
    ###########################################################################

    ###########################################################################
    click.echo('Creating `_build/deploy.bash')
    template = env.get_template('deploy.bash.j2')
    content = template.render(**options)
    with open(os.path.join(outdir, 'deploy.bash'), 'wb') as fh:
        fh.write(content)
    click.echo('...done')
    ###########################################################################
