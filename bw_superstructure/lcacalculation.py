﻿import pandas as pd
import pathlib as pt
from typing import Optional, Tuple, Union

from bw_superstructure.export import (
    export_lca_scores,
    create_export_folder,
)
from bw_superstructure.tools import remove_cols_from_sdf
from bw_superstructure.export import check_export_folder_path
from bw_superstructure.superstructure.manager import (
    format_dataframe,
)
from bw_superstructure.superstructure.excel import import_from_excel
from bw_superstructure.superstructure.mlca import (
    SuperstructureMLCA,
    SuperstructureContributions,
)
from bw_superstructure.bwutils.calculations import do_LCA_calculations


def get_scenario_difference_dataframe(
    path_to_SDF: pt.Path, import_sheet: Union[str, int]=0, export_to_excel=False
) -> pd.DataFrame:

    scenario_diff_file = import_from_excel(path_to_SDF, import_sheet)

    scenario_diff_df = format_dataframe(scenario_diff_file)
    scenario_diff_df = remove_cols_from_sdf(
        scenario_diff_df,
        export_to_excel=False,
    )

    print(f"Imported scenario difference file from: {path_to_SDF}")

    return scenario_diff_df


def calculate_lca_results(
    calc_setup_name: str, scenario_diff_df: pd.DataFrame
) -> Tuple[SuperstructureMLCA, SuperstructureContributions, None]:

    # imitating data-dict from AB
    data = {
            "cs_name": calc_setup_name,
            "calculation_type": "scenario",
            # AB also uses "simple" here for non-scenario LCA, see in do_LCA_calculations()
            "data": scenario_diff_df
            }

    print(f"Calculating LCA results for calculation setup: {calc_setup_name} .....")
    mlca, contributions, mc = do_LCA_calculations(data)

    return mlca, contributions, mc


def calculate_scenario_LCA(
    calc_setup_name: str,
    path_to_SDF: pt.Path,
    sdf_sheet: Union[str, int]=0,
    export_results_to_excel=True,
    fp_export_lca_results: Optional[pt.Path] = None,  #: pt.Path,
    fp_lcia_methods: Optional[pt.Path] = None,
):

    if export_results_to_excel:
        fp_export_lca_results = check_export_folder_path(
            fp_export_folder=fp_export_lca_results
        )  # we check early whether the export folder is already existing to reduce waiting time for the user

    scenario_diff_df = get_scenario_difference_dataframe(
        path_to_SDF, import_sheet=sdf_sheet
    )
    mlca, contributions, mc = calculate_lca_results(calc_setup_name, scenario_diff_df)

    if export_results_to_excel:
        export_lca_scores(mlca, fp_export_lca_results, fp_lcia_methods)

    return mlca, contributions, mc
