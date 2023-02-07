import pandas as pd
import pathlib as pt
import brightway2 as bw

from .superstructure.manager import (
    format_dataframe,
)

from .bwutils.calculations import do_LCA_calculations
from .superstructure.excel import import_from_excel
from .superstructure.mlca import (
    SuperstructureMLCA,
    SuperstructureContributions,
)

from .export import (
    create_excel_filename,
    create_excelsheet_calc_setup,
    create_excelsheet_impacts,
    write_lcaresults_to_excel,
)
from .tools import remove_cols_from_sdf


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


def export_lca_scores(mlca, fp_lca_results):

    scenarios = [iscen for iscen in mlca.scenario_names]
    impact_categories = [", ".join(bw.Method(imeth).name) for imeth in mlca.methods]
    impact_cat_units = [bw.Method(imeth).metadata["unit"] for imeth in mlca.methods]

    # loop over results and save lca results for each FU in an excel workbookk
    for idx_fu, ifu_label in enumerate(mlca.func_units):

        ifu_act = list(ifu_label.keys())[
            0
        ]  # actual bw-object of the bw2_activity for the fu, needed to get access to db
        ifu_amount = list(ifu_label.values())[0]

        # filename
        ifile_name = create_excel_filename(ifu_act)

        df_calc_setup = create_excelsheet_calc_setup(ifu_act, ifu_amount)

        df_impacts = create_excelsheet_impacts(
            mlca, idx_fu, impact_categories, impact_cat_units, scenarios
        )

        write_lcaresults_to_excel(fp_lca_results, ifile_name, df_calc_setup, df_impacts)

    print(
        f"Exported LCA results into {idx_fu+1} excel files to: {fp_lca_results}",
    )


def calculate_scenario_LCA(
    calc_setup_name: str,
    path_to_SDF: pt.Path,
    sdf_sheet_idx=0,
    export_results_to_excel=True,
    fp_export_lca_results=pt.Path("./exports"),
):

    scenario_diff_file = get_scenario_difference_dataframe(
        path_to_SDF, sheet_idx=sdf_sheet_idx
    )
    mlca, contributions, mc = calculate_lca_results(calc_setup_name, scenario_diff_file)

    if export_results_to_excel:
        export_lca_scores(mlca, fp_export_lca_results)

    return mlca, contributions, mc
