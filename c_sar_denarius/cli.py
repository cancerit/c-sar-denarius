import logging
import os
import sys

import click
import pkg_resources  # part of setuptools
from click_option_group import OptionGroup

LOG_LEVELS = ("WARNING", "INFO", "DEBUG")
HIDE_SSL_OPTIONS = True


def _log_setup(loglevel):
    logging.basicConfig(level=getattr(logging, loglevel.upper()), format="%(levelname)s: %(message)s")


def serve_opts(function):
    function = click.option(
        "-t",
        "--target",
        required=True,
        type=click.Path(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
        help="Same as target used when generating results",
    )(function)
    return function


optgroup_debug = OptionGroup("\nDebug options", help="Options specific to troubleshooting, testing")

optgroup_serve = OptionGroup("\nServer options", help="Options specific to serving the website")


@click.group()
@click.version_option(pkg_resources.require(__name__.split(".")[0])[0].version)
def cli():
    pass


@cli.command()
@serve_opts
@optgroup_serve.option(
    "-a",
    "--authfile",
    required=False,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
    help="group/pw in yaml for auth protecting served data [cancer/test]",
)
@optgroup_serve.option(
    "-p",
    "--port",
    required=False,
    default=8000,
    type=click.IntRange(1024, 32768),
    help="Port of this host to serve data on.",
)
@optgroup_serve.option(
    "-s",
    "--ssl",
    required=False,
    is_flag=True,
    help="Use https, requires ~/.ssh/{cert,key}.pem",
    hidden=HIDE_SSL_OPTIONS,
)
@optgroup_debug.option(
    "-l",
    "--loglevel",
    required=False,
    default="INFO",
    show_default=True,
    type=click.Choice(LOG_LEVELS, case_sensitive=False),
    help="Set logging verbosity",
)
def server(target, authfile, port, loglevel, ssl):
    """
    Serve the result of a pre-generated output.
    """
    _log_setup(loglevel)
    serve.site(target, authfile, port, ssl)
