import logging
import os
import sys
from functools import wraps

import click
import pkg_resources  # part of setuptools
from click_option_group import OptionGroup

from c_sar_denarius.constants import DEFAULT_GRP
from c_sar_denarius.constants import DEFAULT_PW

LOG_LEVELS = ("WARNING", "INFO", "DEBUG")
HIDE_SSL_OPTIONS = True

optgroup_debug = OptionGroup("\nDebug options", help="Options specific to troubleshooting, testing")
optgroup_serve = OptionGroup("\nServer options", help="Options specific to serving the website")


def _log_setup(loglevel):
    logging.basicConfig(level=getattr(logging, loglevel.upper()), format="%(levelname)s: %(message)s")


def _dir_exists():
    return click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    )


def input_opts(f):
    @click.option(
        "-i",
        "--input",
        required=True,
        type=_dir_exists(),
        help="c-sar result folder",
    )
    @click.option(
        "-n",
        "--name",
        required=True,
        type=str,
        help="Name to apply to results in interface menu.",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def output_opts(f):
    @click.option(
        "-t",
        "--target",
        required=True,
        type=click.Path(
            exists=False,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
        help="Where site will be generated, can add new result sets.",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def serve_opts(f):
    @optgroup_serve.option(
        "-a",
        "--authfile",
        required=False,
        type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
        help=f"group/pw in yaml for auth protecting served data [{DEFAULT_GRP}/{DEFAULT_PW}]",
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
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def debug_opts(f):
    @optgroup_debug.option(
        "-l",
        "--loglevel",
        required=False,
        default="INFO",
        show_default=True,
        type=click.Choice(LOG_LEVELS, case_sensitive=False),
        help="Set logging verbosity",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


@click.group()
@click.version_option(pkg_resources.require(__name__.split(".")[0])[0].version)
def cli():
    pass


@cli.command()
@output_opts
@serve_opts
@debug_opts
def server(target, authfile, port, loglevel, ssl):
    """
    Serve the result of a pre-existing target area.
    """
    _log_setup(loglevel)
    serve.site(target, authfile, port, ssl)


@cli.command()
@input_opts
@output_opts
@debug_opts
def markdown(loglevel):
    """
    Generate (or extend existing) c-sar-denarius site from a c-sar result folder.
    """
    _log_setup(loglevel)
    # main.test_markdown(output, title, config, mode, nf_tsv)
