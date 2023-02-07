import bw_superstructure as bwss
import brightway2 as bw
import pathlib as pt

########
project_name = "fritsb"

db_original_name = "eco_export"
db_name_relinked = "eco_export_SS"
db_name_old_bg = "ecoinvent38_cutoff"
db_name_new_bg = "SS_ei38_remind_Base_RCP19_SETAC2022"
create_new_db_relinked = True
calc_setup_name = "bw_ss_test"

fp_functional_units = pt.Path("./example/inputs/functional_units.xlsx")
fp_lcia_methods = pt.Path("./example/inputs/lcia_methods.yaml")

path_to_SDF = pt.Path(
    "./example/inputs/scenario_diff_SS_ei38_remind_Base_RCP19_2022.xlsx"
)

export_results_to_excel = True
fp_export_lca_results = pt.Path("./example/exports")


######### LCA calculation

bw.projects.set_current(project_name)

bwss.relink_database_to_new_background(
    db_original_name,
    db_name_relinked,
    db_name_old_bg,
    db_name_new_bg,
    create_new_db_relinked=create_new_db_relinked,
)


bwss.create_calculation_setup(
    db_original_name,  
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
