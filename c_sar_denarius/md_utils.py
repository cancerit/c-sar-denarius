import csv
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import List

from pkg_resources import resource_filename

import c_sar_denarius.utils as csd_utils

MKDOCS_BUILD = "cd %(md_base)s && mkdocs build -d %(tmp_target)s && rsync -ar %(tmp_target)s/* %(target)s"


def mkdocs_base(target):
    logging.info(f"Building site into: {target}")
    md_base = os.path.join(target, "md")
    os.makedirs(os.path.join(md_base, "docs"), exist_ok=True)
    mkdocs_yml = resource_filename(__name__, "resources/templates/mkdocs.yml")
    shutil.copyfile(mkdocs_yml, os.path.join(md_base, "mkdocs.yml"))
    index_md = resource_filename(__name__, "resources/templates/index.md.tmpl")
    shutil.copyfile(index_md, os.path.join(md_base, "docs", "index.md"))
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


def archive_files_to_md(archive_path: str):
    file_list_md = f"## Complete outputs\n\n[Download archive]({archive_path}), this is for the analysis as a whole, not just this sample grouping.\n\n"
    return file_list_md


def title_and_ver(title, c_sar_version, config_ver):
    md_str = f"# {title}\n\n"
    md_str = f"## Versions\n\n"
    md_str += f"* {c_sar_version} : c-sar ('?' indicates unable to detect)\n"
    md_str += f"* {csd_utils.version()} : c-sar-denarious\n"
    md_str += f"* {config_ver} : c-sar-denarious config\n"
    # no trailing new lines
    return md_str


def result_archive(output: str, archive_clean: List[str], title: str):
    files_path = os.path.join(output, "docs", title, "files")
    minimise_result_data(files_path, archive_clean)

    tar_dest = os.path.join(files_path, "results.tar.gz")
    logging.info(f"Building archive: {tar_dest}")
    with tempfile.TemporaryDirectory(prefix=__name__) as tmpdir:
        tmp_tar = os.path.join(tmpdir, "results.tar.gz")
        # dereference=False to allow symlinks
        with tarfile.open(name=tmp_tar, mode="w:gz", dereference=False) as tar:
            tar.add(files_path, arcname=".")
        shutil.move(tmp_tar, tar_dest)

    # remove files only needed in archive
    for f in archive_clean:
        os.remove(f)


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


def minimise_result_data(files_path: str, archive_clean: List[str]):
    logging.info(f"Minimizing data files under: {files_path}")
    # need to be careful of links depending on this
    chksums = {}
    # symlinks need to have a base of in the 'files' subdir
    for dirpath, dirnames, filenames in os.walk(files_path):
        for name in filenames:
            item = os.path.join(dirpath, name)
            digest = csd_utils.sha256(item)
            if digest not in chksums:
                chksums[digest] = []
            chksums[digest].append(item)

    to_clean_set = set(archive_clean)

    for digest, files in chksums.items():
        if len(files) == 1:
            continue
        # Need to make sure that we only use files that aren't about to be deleted as the "real" file
        safe_files = set(files).difference(to_clean_set)
        real = None
        if len(safe_files) == 0:
            # If all files are to deleted after archive is built we can use any
            real = files[0]
        else:
            # to be consistent sort this
            real = sorted(safe_files)[0]
        real = real.replace(files_path + "/", "")

        for f in files[1:]:
            rel_dirs = f.replace(files_path + "/", "").count("/")
            link_path = os.path.join("../" * rel_dirs, real)
            os.unlink(f)
            os.symlink(link_path, f)
