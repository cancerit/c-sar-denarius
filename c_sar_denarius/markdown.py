# import c_sar_denarius.utils as csdutils
# def structure_yaml(root:str):
#     # we need to know ?_vs_?
#     comparison_type = mode_from_nf_manifest(nf_tsv)
#     # load the raw string
#     md_template = resource_string(
#         __name__, f"resources/structure/{conf_name}/{structure_type}.yaml"
#     ).decode("utf-8", "strict")
#     # deal with the way we have to handle the folders with treatment/plasmid/control
#     return yaml.safe_load(md_template.replace("%A%_vs_%B%", comparison_type))
# def result_to_md():
#     pass
