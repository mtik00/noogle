import os
import click
import ruamel.yaml
import glob


def get_template(name):
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))
    with open(os.path.join(template_dir, name)) as fh:
        text = fh.read()

    return text


@click.command()
def build():
    """
    Build the utility
    """
    from ...settings import DEPLOY_CONFIG_PATH

    instance_dirname = "instance"
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    instance_dir = os.path.abspath(os.path.join(base_dir, instance_dirname))
    outdir = os.path.join(base_dir, "_build")

    if not os.path.exists(DEPLOY_CONFIG_PATH):
        click.echo("ERROR: Could not find %s" % DEPLOY_CONFIG_PATH)
        click.echo("...a sample is located in `conf`")
        click.echo(
            "...copy `conf/deploy-sample.yaml` to your instance folder as `instance/config/deploy.yaml`, and modify it as needed"
        )
        click.echo("...we think your instance folder is here: " + instance_dir)
        raise click.Abort()

    options = ruamel.yaml.safe_load(open(DEPLOY_CONFIG_PATH).read())
    options["circus_ini"] = os.path.join(instance_dir, "circus.ini")
    options["instance_dirname"] = instance_dirname
    options["env_sh"] = os.path.join(instance_dir, "env.sh")

    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    else:
        files = glob.glob(f"{outdir}/*")
        for f in files:
            os.unlink(f)

    ###########################################################################
    click.echo("Creating `_build/noogle-systemd.service")
    template = get_template("noogle-systemd.service")
    content = template.format(**options)
    with open(os.path.join(outdir, "noogle-systemd.service"), "wb") as fh:
        fh.write(content.encode("utf-8"))
    click.echo("...done")
    ###########################################################################

    ###########################################################################
    click.echo("Creating `_build/deploy.bash")
    template = get_template("deploy.bash")
    content = template.format(**options)
    with open(os.path.join(outdir, "deploy.bash"), "wb") as fh:
        fh.write(content.encode("utf-8"))
    click.echo("...done")
    ###########################################################################

    ###########################################################################
    click.echo("Creating `_build/circus.ini")
    template = get_template("circus.ini")
    content = template.format(**options)
    with open(os.path.join(outdir, "circus.ini"), "wb") as fh:
        fh.write(content.encode("utf-8"))
    click.echo("...done")
    ###########################################################################
