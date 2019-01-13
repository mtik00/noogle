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
    from ...settings import DEPLOY_CONFIG_PATH, INSTANCE_FOLDER, CIRCUS_INI_PATH

    instance_dirname = "instance"
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    outdir = os.path.join(base_dir, "_build")

    if not os.path.exists(DEPLOY_CONFIG_PATH):
        click.echo("ERROR: Could not find %s" % DEPLOY_CONFIG_PATH)
        click.echo("...a sample is located in `conf`")
        click.echo(
            "...copy `conf/deploy-sample.yaml` to your instance folder as `instance/config/deploy.yaml`, and modify it as needed"
        )
        click.echo("...we think your instance folder is here: " + INSTANCE_FOLDER)
        raise click.Abort()

    options = ruamel.yaml.safe_load(open(DEPLOY_CONFIG_PATH).read())
    options["circus_ini"] = CIRCUS_INI_PATH
    options["instance_dirname"] = instance_dirname
    options["env_sh"] = os.path.join(INSTANCE_FOLDER, "env.sh")
    options["rotate_log_size"] = options.get("rotate_log_size_mb", 10) * 2 ** 20
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
