﻿import brightway2 as bw
import pathlib as pt

import bw_superstructure as bwss
from bw_superstructure.export import (
    check_export_folder_path,
)


######### Input paramaters
project_name = "fritsb"  # name of an existing bw2-project

db_original_name = (
    "eco_export"  # name of an existing db, which can be relinked to another BG-DB
)
db_name_relinked = (
    "eco_export_SS"  # name if the original db was relinked and newly created
)
create_new_db_relinked = True  # if True, an already existing DB with the name of db_name_relinked will be deleted, and a new db_name_relinked will be created. if False, the already existing DB of the name db_name_relinked will be used

db_name_old_bg = (
    "ecoinvent38_cutoff"  # name of the old (i.e. current)  BG-DB of the original DB
)

db_name_new_bg = "SS_ei38_remind_Base_RCP19_SETAC2022"  # name of the new BG-DB which the original DB will be relinked to
fp_import_new_bg_db = None  # pt.Path("C:/Users/.../SS_ei38_remind_Base_RCP19_SETAC2022.xlsx")  # default=None # optional # if new BG-DB is not yet existing in project as a bw-DB, it can be imported from an excel or ecospold file. Provide a filepath to those files. Otherwise, set to None
filetype_import_new_bg_db = None  # "excel" or "ecospold"; default=None # optional # file type of the file which the new BG-DB needs to be imported from

calc_setup_name = "bw_ss_test"  # name of the calculation setup

# input files and their filepaths
fp_functional_units = pt.Path(
    "./example/inputs/functional_units.xlsx"
)  # filepath to functional units for the calculation setup
fp_lcia_methods = pt.Path(
    "./example/inputs/lcia_methods.yaml"
)  # filepath to the lcia methods (impact categories) for the calculation setup
path_to_SDF = pt.Path(
    "./example/inputs/scenario_diff_SS_ei38_remind_Base_RCP19_2022.xlsx"
)  # filepath to the scenario difference file for the scenario LCA, e.g. as generated by premise

# export of LCA results
export_results_to_excel = True  # True: scenario LCA scores will be exported to exports or the filepath given in fp_export_lca_results
fp_export_lca_results = None  # if None, a default is created in the export folder using a time-stamp for the folder name
# fp_export_lca_results = pt.Path(
#     "./example/exports/my_example_case"
# )  # optional; if not provided, the default is the exports folder


######### LCA calculation

bw.projects.set_current(project_name)

# we first check the export folder path, such that we do not run into an error at the very end (this is optional)
if export_results_to_excel:
    fp_export_lca_results = check_export_folder_path(fp_export_lca_results)

bwss.relink_database_to_new_background(
    db_original_name,
    db_name_relinked,
    db_name_old_bg,
    db_name_new_bg,
    create_new_db_relinked=create_new_db_relinked,
    fp_import_new_bg_db=fp_import_new_bg_db,  # None 
    filetype_import_new_bg_db=filetype_import_new_bg_db,  # None
)  # relinking the DB is optional,


bwss.create_calculation_setup(
    calc_setup_name,
    fp_functional_units,
    fp_lcia_methods,
)  # creates a calculation set-up with the functional units and the LCIA methods as specified in the respective input files

mlca, contributions, mc = bwss.calculate_scenario_LCA(
    calc_setup_name,
    path_to_SDF,
    export_results_to_excel=export_results_to_excel,
    fp_export_lca_results=fp_export_lca_results,
)  # calculates the LCA results for all functional units, LCIA methods and scenarios (as specified in the scenario difference file)

# if desired, the user can export the LCA-results via a separate function:
# bwss.export_lca_scores(
#     mlca, fp_export_lca_results=pt.Path("./example/exports/mytest")
# )
