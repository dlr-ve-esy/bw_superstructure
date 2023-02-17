import pandas as pd
import pathlib as pt
from typing import Optional

from bw_superstructure.export import (
    export_lca_scores,
    create_export_folder,
)
from bw_superstructure.tools import remove_cols_from_sdf
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
    path_to_SDF: pt.Path, sheet_idx=0, export_to_excel=False
) -> pd.DataFrame:

    scenario_diff_file = import_from_excel(path_to_SDF, sheet_idx)

    scenario_diff_df = format_dataframe(scenario_diff_file)
    scenario_diff_df = remove_cols_from_sdf(
        scenario_diff_df,
        export_to_excel=False,
    )

    return scenario_diff_df


def calculate_lca_results(
    calc_setup_name: str, scenario_diff_df: pd.DataFrame
) -> (SuperstructureMLCA, SuperstructureContributions, None):

    # imitating data-dict from AB
    data = {}

    data["cs_name"] = calc_setup_name
    data[
        "calculation_type"
    ] = "scenario"  # AB also uses "simple" here for non-scenario LCA, see in do_LCA_calculations()
    data["data"] = scenario_diff_df

    mlca, contributions, mc = do_LCA_calculations(data)

    return mlca, contributions, mc


def calculate_scenario_LCA(
    calc_setup_name: str,
    path_to_SDF: pt.Path,
    sdf_sheet_idx=0,
    export_results_to_excel=True,
    fp_export_lca_results: Optional[pt.Path] = None,  #: pt.Path,
):
    
    if export_results_to_excel:
        fp_export_lca_results = create_export_folder(
            fp_export_folder=fp_export_lca_results
        )  # we check early whether the export folder is already existing to reduce waiting time for the user 

    scenario_diff_file = get_scenario_difference_dataframe(
        path_to_SDF, sheet_idx=sdf_sheet_idx
    )
    mlca, contributions, mc = calculate_lca_results(calc_setup_name, scenario_diff_file)

    if export_results_to_excel:
        export_lca_scores(mlca, fp_export_lca_results)

    return mlca, contributions, mc
