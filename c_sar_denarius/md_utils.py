import csv
import logging
import os
import shutil
import subprocess
import tempfile
from typing import List

from pkg_resources import resource_filename
from pkg_resources import resource_string

import c_sar_denarius.utils as csd_utils

MKDOCS_BUILD = "cd %(md_base)s && mkdocs build -d %(tmp_target)s && rsync -ar %(tmp_target)s/* %(target)s"


def mkdocs_base(target, primary_color: "blue-grey"):
    logging.info(f"Building site into: {target}")
    md_base = os.path.join(target, "md")
    # lazily creating structure
    os.makedirs(os.path.join(md_base, "docs", "stylesheets"), exist_ok=True)

    mkdocs_yml = resource_string(__name__, f"resources/templates/mkdocs.yml.tmpl").decode("utf-8", "strict")
    mkdocs_yml = mkdocs_yml.replace("%primary-colour%", primary_color.replace("-", " "))
    with open(os.path.join(md_base, "mkdocs.yml"), "wt") as mdy:
        print(mkdocs_yml, file=mdy)

    index_md = resource_filename(__name__, "resources/templates/index.md.tmpl")
    shutil.copyfile(index_md, os.path.join(md_base, "docs", "index.md"))
    index_md = resource_filename(__name__, "resources/other/denarius.png")
    shutil.copyfile(index_md, os.path.join(md_base, "docs", "denarius.png"))
    index_md = resource_filename(__name__, "resources/other/denarius.css")
    shutil.copyfile(index_md, os.path.join(md_base, "docs", "stylesheets", "denarius.css"))
    return md_base


def file_to_md_table(f_path: str):
    qc_table = ""
    with open(f_path, "r", newline="\n") as csvfh:
        header = True
        for row in csv.reader(csvfh, delimiter="\t"):
            qc_table += "| " + " | ".join(row) + " |\n"
            if header:
                qc_table += "| " + " | ".join(["---"] * len(row)) + " |\n"
                header = False
    qc_table += "\n"
    return qc_table


def title_and_ver(title, c_sar_version, config_ver):
    md_str = f"# {title}\n\n"
    md_str = f"## Versions\n\n"
    md_str += f"* {c_sar_version} : c-sar ('?' indicates unable to detect)\n"
    md_str += f"* {csd_utils.version()} : c-sar-denarious\n"
    md_str += f"* {config_ver} : c-sar-denarious config\n"
    # no trailing new lines
    return md_str


def mkdocs(md_base, final_build):
    """
    sync the docs into the final tree
    generate the site
    move old content of root out of place
    move new content of root into place
    """
    with tempfile.TemporaryDirectory(prefix=__name__) as tmpdir:
        os.makedirs(final_build, exist_ok=True)
        full_command = MKDOCS_BUILD % {
            "md_base": md_base,
            "tmp_target": tmpdir,
            "target": final_build,
        }
        logging.info(f"Generating markdown site, executing: {full_command}")
        r = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            csd_utils.process_log_and_exit(r, "Problem while building mkdocs site")
