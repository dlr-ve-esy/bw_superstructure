import pandas as pd
import datetime

from .superstructure.mlca import (
    SuperstructureMLCA,
)


def create_excel_filename(bw2_activity):
    "For exporting LCA results for a functional unit"
    file_name = (
        bw2_activity["reference product"]
        + "_"
        + bw2_activity["name"]
        + "_"
        + bw2_activity["location"]
        + "_"
        + bw2_activity["database"]
        + ".xlsx"
    )

    return file_name


def create_excelsheet_calc_setup(bw2_activity, fu_amount: int):
    "For exporting LCA results. This functions creates and fills the excel sheet called 'calculation setup'."

    df = pd.DataFrame(
        [
            [
                "Reference product",
                "Process",
                "Location",
                "Unit",
                "Amount",
                "Database",
                "Date",
            ],
            [
                bw2_activity["reference product"],
                bw2_activity["name"],
                bw2_activity["location"],
                bw2_activity["unit"],
                fu_amount,
                bw2_activity["database"],
                datetime.datetime.now().replace(microsecond=0),
            ],
        ],
    )

    df = df.T
    df.set_index(list(df.columns)[0], inplace=True)

    return df


def create_excelsheet_impacts(
    mlca: SuperstructureMLCA,
    idx_fu: int,
    impact_categories,
    impact_cat_units,
    scenarios,
):
    "For exporting LCA results. This functions creates and fills the excel sheet called 'Imapcts'."

    data = pd.DataFrame(index=impact_categories)

    data["Unit"] = impact_cat_units
    # Note: add here something shorter, e.g. method abbreviation, use MethodTuple?

    data_lcascores = pd.DataFrame(
        mlca.lca_scores[idx_fu], columns=scenarios, index=impact_categories
    )

    data = pd.concat([data, data_lcascores], axis="columns")
    data.index.name = "Impact category"

    return data


def write_lcaresults_to_excel(
    fp_lca_results, ifile_name, df_calculationsetup, df_impacts
):
    "For exporting LCA results. This functions creates a workbook per functional unit with the 2 excel sheets called 'Calculation setup' and 'Imapcts'."

    iwriter = pd.ExcelWriter(fp_lca_results / ifile_name)
    df_calculationsetup.to_excel(
        iwriter, sheet_name="Calculation setup", index=True, header=False
    )
    df_impacts.to_excel(iwriter, sheet_name="Impacts", index=True)

    iwriter.save()
