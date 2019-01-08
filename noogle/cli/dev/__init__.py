import click

from .build import build


@click.group(name="dev")
def dev():
    """Development Tools"""
    ctx = click.get_current_context()

    # No reason to continue if we're in quiet mode
    if ctx.obj.quiet:
        ctx.exit()


dev.add_command(build)
