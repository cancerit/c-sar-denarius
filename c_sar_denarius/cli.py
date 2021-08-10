import logging
import os
import sys
from functools import wraps

import click
from click_option_group import OptionGroup

import c_sar_denarius.serve as csd_serve
from c_sar_denarius import markdown as csd_md
from c_sar_denarius.constants import DEFAULT_GRP
from c_sar_denarius.constants import DEFAULT_PW
from c_sar_denarius.utils import version

LOG_LEVELS = ("WARNING", "INFO", "DEBUG")
HIDE_SSL_OPTIONS = True
MKDOCS_PC = (
    "red",
    "pink",
    "purple",
    "deep-purple",
    "indigo",
    "blue",
    "light-blue",
    "cyan",
    "teal",
    "green",
    "light-green",
    "lime",
    "yellow",
    "amber",
    "orange",
    "deep-orange",
    "brown",
    "grey",
    "blue-grey",
    "black",
    "white",
)

optgroup_debug = OptionGroup("\nDebug options", help="Options specific to troubleshooting, testing")
optgroup_serve = OptionGroup("\nServer options", help="Options specific to serving the website")


def log_setup(loglevel):
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
    @click.option(
        "-c",
        "--primary-color",
        required=True,
        type=click.Choice(MKDOCS_PC, case_sensitive=False),
        default="blue-grey",
        help="Primary color (header/text) in generated website",
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
@click.version_option(version())
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
    log_setup(loglevel)
    csd_serve.site(target, authfile, port, ssl)


@cli.command()
@input_opts
@output_opts
@debug_opts
def markdown(*args, **kwargs):
    """
    Generate (or extend existing) c-sar-denarius site from a c-sar result folder.
    """
    csd_md.run(*args, **kwargs)
