﻿import brightway2 as bw
import pathlib as pt

import bw_superstructure as bwss
from bw_superstructure.export import (
    check_export_folder_path,
    export_lca_scores,
)
from bw_superstructure.superstructure.importer import ScenarioImporter
from bw_superstructure.bwutils.calculations import do_LCA_calculations


######### Input paramaters
project_name = "db_eco38"  # name of an existing bw2-project

calc_setup_name = "bw_scenario_test"  # name of the calculation setup

# input files and their filepaths
# filepath to functional units for the calculation setup
fp_functional_units = pt.Path("./example/inputs/functional_units_sander.xlsx")
# filepath to the lcia methods (impact categories) for the calculation setup
fp_lcia_methods = pt.Path("./example/inputs/lcia_methods.yaml")
# filepath to the scenario difference file for the scenario LCA, e.g. as generated by premise
path_to_SDF = pt.Path("./example/inputs/combined_scenario.xlsx") #Old: scenario_diff_SS_ei38_remind_Base_RCP19_2022.xlsx"

# export of LCA results
export_results_to_excel = True  # True: scenario LCA scores will be exported to exports or the filepath given in fp_export_lca_results
# if None, a default is created in the export folder using a time-stamp for the folder name
fp_export_lca_results = pt.Path("./example/exports/mytest")

additional_functional_units = [("heat, future",	"wood pellets, burned in stirling heat and power co-generation unit, 3kW electrical, future", "CH",	"ecoinvent38_cutoff"),
                               ("electricity, high voltage", "electricity production, nuclear, boiling water reactor_4BioG_OpO", "DE", "eco_export_SS")]


######### LCA calculation

bw.projects.set_current(project_name)

# we first check the export folder path, such that we do not run into an error at the very end (this is optional)
if export_results_to_excel:
    fp_export_lca_results = check_export_folder_path(fp_export_lca_results)

# Load scenario files and export as single scenario
tables = ScenarioImporter()
base = "C:/Users/nielenssvan/OneDrive - Universiteit Leiden/D7_3/bw-AB/"
tables.load_scenarios([(base+"PFS-waste-input.xlsx", 1),
                    (base+"upscaling_flow-scenarios.xlsx", 3),
                    (base+"PFS-demonstrators.xlsx", 3)], #6 = sintered magnet
                    "product")
tables.scenario_df.to_excel(path_to_SDF, index=True, merge_cells=False)

bwss.create_calculation_setup(
    calc_setup_name,
    fp_lcia_methods,
    fp_functional_units=fp_functional_units,
    # additional_functional_units=additional_functional_units,
)  # creates a calculation set-up with the functional units and the LCIA methods as specified in the respective input files

mlca, contributions, mc = do_LCA_calculations({"cs_name": calc_setup_name,
                    "calculation_type": "scenario", "data": tables.scenario_df})

# if desired, the user can export the LCA-results via a separate function:
if export_results_to_excel:
    export_lca_scores(mlca, fp_export_lca_results)