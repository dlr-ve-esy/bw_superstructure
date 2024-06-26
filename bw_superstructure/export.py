﻿import pandas as pd
import datetime
import pathlib as pt
from collections import defaultdict
from typing import Optional

import brightway2 as bw
from bw_superstructure.calculationsetup import get_lcia_methods

from bw_superstructure.superstructure.mlca import (
    SuperstructureMLCA,
)
from bw_superstructure.tools import time_stamp


def check_export_folder_path(fp_export_folder: Optional[pt.Path] = None) -> pt.Path:
    """Checks whether a folder already exists for the given filepath or creates a new default filepath for exporting LCA scores.

    By default (fp_export_folder=None, i.e. no user-specific path is specified), the folder name is the time it gets created.
    For fp_export_folder, the user can either provide a specific pt.Path or a string which will be converted into a pt.Path.
    If the folder exists already, an Error is raised. If it doesn't, a filepath is returned.

    Args:
        fp_export_folder (pt.Path or str, optional): Filepath to folder to which LCA results should be exported to (excel files). Default is None.

    Returns:
        fp_export_folder (pt.Path): Filepath to folder to which LCA results should be exported to (excel files).
    """

    if not fp_export_folder:  # default folder if None
        timenow = time_stamp()

        # create directories if they don't yet exist:
        working_dir = pt.Path(".")
        # print(working_dir.absolute())
        fp_export_folder = working_dir / "exports" / timenow

    else:  # user-specific folder path
        fp_export_folder = pt.Path(fp_export_folder)

    if fp_export_folder.exists():
        raise IOError(
            f"Folder {fp_export_folder.absolute()} is already there. We do not override the folder. Please delete the existing one or specify another folder"
        )

    return fp_export_folder


def create_export_folder(fp_export_folder: Optional[pt.Path] = None) -> pt.Path:
    """Creates a folder for exporting the excel files containing LCA scores for each functional unit.
    By default (fp_export_folder=None, i.e. no user-specific path is specified), the folder name is the time it gets created.

    For fp_export_folder, the user can either provide a specific pt.Path or a string which will be converted into a pt.Path.

    If the folder exists already, an Error is raised. If it doesn't, a new folder will be created.

    Args:
        fp_export_folder (pt.Path or str, optional): Filepath to folder to which LCA results should be exported to (excel files). Defaults to None.

    Returns:
        fp_export_folder (pt.Path): Filepath to folder to which LCA results should be exported to (excel files).
    """

    fp_export_folder = check_export_folder_path(fp_export_folder)

    fp_export_folder.mkdir(parents=True, exist_ok=False)

    print(f"Created export folder: {fp_export_folder.absolute()}")

    return fp_export_folder


def create_excel_filename(
    act_details: tuple, fu_name_counts: defaultdict
) -> tuple[str, defaultdict]:
    """creates a human-readable name for an excel file based on the activity details. This name usually contains the first word of the reference product, the process name, and the DB-name. If the name is non-unique, numbers are added to the name to distinguish the different names.

    Args:
        act_details (tuple): contains strings for the activity details, e.g. ref-product, process name, location, DB-name
        fu_name_counts (defaultdict): counts the occurrences of the activity details.

    Returns:
        ifile_name, fu_name_counts (tuple[str, defaultdict]): a str of the act_details, and a dictionary for counting occurrences.
    """

    assert isinstance(
        act_details, tuple
    ), f"object act_details is not of type 'tuple' but of type: {type(act_details)}"
    assert (
        len(act_details) > 0
    ), f'object act_details is empty. It should be a tuple containing several strings for at least: "act-name", "act-location", "act-DB"'

    filename = "_".join(act_details)

    fu_name_counts[
        filename
    ] += 1  # if key is not existing yet, it creates a key with value 0; and does +1 = 1

    icount = fu_name_counts[filename]

    act_details = list(act_details)

    # if same tuples exist, we add a number to the filename, to distinguish the names
    if icount > 1:
        act_details.insert(-1, str(icount))

    filename = "_".join(act_details)

    ifile_name = filename + ".xlsx"

    return ifile_name, fu_name_counts


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
    impact_categories: list,
    impact_cat_units: list,
    scenarios: list,
    impact_categories_internal_names: list, 
    impact_categories_abbreviations: list,
):
    "For exporting LCA results. This functions creates and fills the excel sheet called 'Imapcts'."

    data = pd.DataFrame(index=impact_categories)

    data["Category name short"] = impact_categories_internal_names
    data["Category abbreviated"] = impact_categories_abbreviations

    data["Unit"] = impact_cat_units

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

    try:
        iwriter.save()  # for older pandas versions
    except:
        iwriter._save() # for newer pandas versions


def export_lca_scores(mlca, fp_export_lca_results: Optional[pt.Path] = None, fp_lcia_methods: Optional[pt.Path] = None):

    fp_export_lca_results = create_export_folder(fp_export_lca_results)

    scenarios = [iscen for iscen in mlca.scenario_names]
    
    impact_categories_bw2 = [bw.Method(imeth).name for imeth in mlca.methods] # tuple(str, str, str) e.g. ("IPCC 2013", "climate change", "GWP 100a")
    impact_categories = [", ".join(imeth) for imeth in impact_categories_bw2]
    impact_cat_units = [bw.Method(imeth).metadata["unit"] for imeth in mlca.methods]
    
    # we retrieve some additional information (shorter names and abbreviations) for the lcia methods to write it into the exported excel files
    lcia_methods = get_lcia_methods(fp_lcia_methods)
    lcia_methods_reversed = {method.bw2_object: (method.internal_name, method.internal_abbreviation) for (key, method) in lcia_methods.items()}
    impact_categories_internal_names = []
    impact_categories_abbreviations = []
    
    for imeth in impact_categories_bw2:
        if imeth in lcia_methods_reversed:
            impact_categories_internal_names.append(lcia_methods_reversed[imeth][0])
            impact_categories_abbreviations.append(lcia_methods_reversed[imeth][1])
            

    fu_name_counts = defaultdict(lambda: 0)
    # initialize with 0, and later do +1

    # loop over results and save lca results for each FU in an excel workbook
    idx_fu = 0
    for idx_fu, ifu_label in enumerate(mlca.func_units):

        ifu_act = list(ifu_label.keys())[
            0
        ]  # actual bw-object of the bw2_activity for the fu, needed to get access to db
        ifu_amount = list(ifu_label.values())[0]

        iact_details = (
            ifu_act["reference product"].split()[0].strip(","),
            ifu_act["name"],
            ifu_act["location"],
            ifu_act["database"],
        )

        ifile_name, fu_name_counts = create_excel_filename(iact_details, fu_name_counts)

        df_calc_setup = create_excelsheet_calc_setup(ifu_act, ifu_amount)

        df_impacts = create_excelsheet_impacts(
            mlca, idx_fu, impact_categories, impact_cat_units, scenarios, impact_categories_internal_names, impact_categories_abbreviations
        )

        write_lcaresults_to_excel(
            fp_export_lca_results,
            ifile_name,
            df_calc_setup,
            df_impacts,
        )

    print(
        f"Exported LCA results into {idx_fu+1} excel files to: {fp_export_lca_results.absolute()}",
    )
