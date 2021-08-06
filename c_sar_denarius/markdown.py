import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple

import yaml
from pkg_resources import resource_string

from c_sar_denarius import cli
from c_sar_denarius import utils as csd_utils
from c_sar_denarius.md_utils import archive_files_to_md
from c_sar_denarius.md_utils import file_to_md_table
from c_sar_denarius.md_utils import mkdocs
from c_sar_denarius.md_utils import mkdocs_base
from c_sar_denarius.md_utils import result_archive
from c_sar_denarius.md_utils import title_and_ver

COMP_TYPES = ("control_vs_plasmid", "treatment_vs_plasmid", "treatment_vs_control")


def structure_yaml(version: str):
    logging.info(f"c-sar version for structure was '{version}'")
    # load the raw string
    md_template = resource_string(__name__, f"resources/structure/{version}.yaml").decode("utf-8", "strict")
    # deal with the way we have to handle the folders with treatment/plasmid/control
    return yaml.safe_load(md_template)


def file_to_md(
    input: str,
    output: str,
    subdir: str,
    title: str,
    item: str,
    image=False,
    table=False,
    required=False,
    label=None,
    download=False,
    wildcard=False,
    description=None,
) -> Tuple[str, List[str]]:
    items = []
    post_archive_rm = []
    full_md = None
    if label is None:
        label = item

    # sample wildcard is only on file name, not folder
    if wildcard:
        pattern = re.compile(item.replace("%S%", "(.+)"))
        for f in os.listdir(os.path.join(input, subdir)):
            m = pattern.fullmatch(f)
            if m is None:
                continue
            (item, sample) = m.group(0, 1)
            if sample == "LFC":
                continue
            items.append({"label": f"{label} - {sample}", "item": item})
    else:
        items.append({"label": label, "item": item})

    for i_dict in items:
        item = i_dict["item"]
        label = i_dict["label"]
        source = os.path.join(input, subdir, item)
        if not os.path.isfile(source):
            if required:
                logging.critical(f"Failed to find file tagged as required: {source}")
                sys.exit(2)
            continue

        if full_md is None:
            full_md = ""

        if table or download or image:
            full_md += f"### {label}\n\n"
            if description:
                full_md += f"{description}\n\n"

        if table:
            full_md += file_to_md_table(source)

        relative = os.path.join("files", subdir, item)
        destination = os.path.join(output, title, relative)
        # all files listed in yaml are copied to files to enable archive building
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copyfile(source, destination)
        if not download and not image:
            post_archive_rm.append(destination)
            # no rendering for these
            continue

        if download:
            full_md += f"[Download](./{relative})\n\n"
        if image:
            full_md += f"![{item}](./{relative})\n\n"
    return (full_md, post_archive_rm)


def build_md(input: str, title: str, target: str, version: str, config_ver: str, structure: Dict):
    """
    As we have "unknown" plasmid_vs_control etc we need to build this from the generic form
    """
    archive_clean = []
    comparison_sets = {}
    output = os.path.join(target, "md", "docs")
    seen_comp_label = {}
    for label in structure:
        for p_subdir in structure[label]:
            # what can we find
            for comparison_type in COMP_TYPES:
                comp_label = f"{comparison_type} - {label}"
                subdir = p_subdir.replace("%A%_vs_%B%", comparison_type)
                for p_item in structure[label][p_subdir]:
                    item = p_item.replace("%A%_vs_%B%", comparison_type)
                    data_file = Path(os.path.join(input, subdir, item))
                    if not data_file.is_file():
                        continue
                    (md_element, post_archive) = file_to_md(
                        input, output, subdir, title, item, **structure[label][p_subdir][p_item]
                    )
                    archive_clean += post_archive
                    if md_element:
                        if comparison_type not in comparison_sets:
                            comparison_sets[comparison_type] = title_and_ver(comparison_type, version, config_ver)

                        if comp_label not in seen_comp_label:
                            comparison_sets[comparison_type] += f"\n\n## {label}"
                            seen_comp_label[comp_label] = None

                        comparison_sets[comparison_type] += f"\n\n{md_element}"

    dest = os.path.join(output, title)
    for comparison_type in comparison_sets:
        # just md generation
        comparison_sets[comparison_type] += archive_files_to_md("./files/results.tar.gz")
        # write the full MD files
        md_file = os.path.join(dest, comparison_type + ".md")
        with open(md_file, "w") as ofh:
            print(comparison_sets[comparison_type], file=ofh)

    # need to unique this list due to looping over comparison types
    return list(set(archive_clean))


def run(input: str, name: str, target: str, loglevel: str):
    cli.log_setup(loglevel)
    (version, config_ver) = csd_utils.c_sar_version(input)
    structure = structure_yaml(version)
    md_base = mkdocs_base(target)
    final_build = os.path.join(target, "site")
    post_archive_clean = build_md(input, name, target, version, config_ver, structure)
    # now build the archive
    result_archive(md_base, post_archive_clean, name)
    mkdocs(md_base, final_build)
