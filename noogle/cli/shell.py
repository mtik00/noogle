import click

from IPython.terminal.embed import InteractiveShellEmbed
from traitlets.config.loader import Config

from ..db import session  # noqa: F401
from ..models import Event  # noqa: F401

cfg = Config()
ipshell = InteractiveShellEmbed(config=cfg)


@click.command()
def shell():
    """
    Run an IPython shell
    """

    ipshell(
        "***Called from top level. "
        "Hit Ctrl-D to exit interpreter and continue program.\n"
        "Note that if you use %kill_embedded, you can fully deactivate\n"
        "This embedded instance so it will never turn on again\n"
        "Try this: session.query(Event).order_by(Event.scheduled_date.desc()).all()"
    )
