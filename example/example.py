import bw_superstructure as bwss
import brightway2 as bw
import pathlib as pt

######## input paramaters
project_name = "fritsb"  # name of a bw2-project

db_original_name = "eco_export"  # name of a db, which can be relinked to another BG-DB
db_name_relinked = (
    "eco_export_SS"  # name if the original db was relinked and newly created
)
db_name_old_bg = (
    "ecoinvent38_cutoff"  # name of the old (i.e. current)  BG-DB of the original DB
)
db_name_new_bg = "SS_ei38_remind_Base_RCP19_SETAC2022"  # name of the new BG-DB which the original DB will be relinked to

create_new_db_relinked = True  # if True, an already existing DB with the name of db_name_relinked will be deleted, and a new db_name_relinked will be created. if False, the already existing DB of the name db_name_relinked will be used

calc_setup_name = "bw_ss_test"  # name of the calculation setup

fp_functional_units = pt.Path(
    "./example/inputs/functional_units.xlsx"
)  # filepath to functional units for the calculation setup
fp_lcia_methods = pt.Path(
    "./example/inputs/lcia_methods.yaml"
)  # filepath to the lcia methods (impact categories) for the calculation setup
path_to_SDF = pt.Path(
    "./example/inputs/scenario_diff_SS_ei38_remind_Base_RCP19_2022.xlsx"
)  # filepath to the scenario difference file for the scenario LCA

export_results_to_excel = True  # True: scenario LCA scores will be exported to the filepath: fp_export_lca_results
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
