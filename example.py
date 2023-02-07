import bw_superstructure as bwss

print("import worked")
########
project_name = ""

db_name = ""
db_name_relinked = ""
db_name_old_bg = ""
db_name_new_bg = ""
create_new_db_relinked = True
calc_setup_name = ""
fp_functional_units = ""
fp_lcia_methods = ""
path_to_SDF = ""

export_results_to_excel = True
fp_export_lca_results = ""


######### LCA calculation


bwss.relink_database_to_new_background(
    db_name,
    db_name_relinked,
    db_name_old_bg,
    db_name_new_bg,
    create_new_db_relinked=create_new_db_relinked,
)


bwss.create_calculation_setup(
    db_name,
    calc_setup_name,
    fp_functional_units,
    fp_lcia_methods,
    db_name_new_bg,
    db_name_ecoinvent="ecoinvent38_cutoff",
)

mlca, contributions, mc = bwss.calculate_scenario_LCA(
    calc_setup_name,
    path_to_SDF,
    export_results_to_excel=True,
    fp_export_lca_results=fp_export_lca_results,
)

