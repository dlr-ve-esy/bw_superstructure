import pandas as pd
import datetime
import brightway2 as bw

from bw_superstructure.bwutils.strategies import relink_exchanges_existing_db
from bw_superstructure.superstructure.utils import SUPERSTRUCTURE


def relink_database_to_new_background(
    db_name: str,
    db_name_relinked: str,
    db_name_old_bg: str,
    db_name_new_bg: str,
    create_new_db_relinked=True,
):

    if create_new_db_relinked:
        # copy original DB, new name
        if db_name_relinked in bw.databases:
            del bw.databases[db_name_relinked]
            print(f"deleted {db_name_relinked}")

        db_relinked_bwobject = bw.Database(db_name).copy(db_name_relinked)

        assert (
            db_name_relinked in bw.databases
        ), f"{db_name_relinked} not in databases: {bw.databases}"

        print(f"created new DB to be relinked: {db_name_relinked}")

        fg_db = bw.Database(
            db_name_relinked
        )  # foreground DB to relink from old background to new background DB
        new_bg_db = bw.Database(
            db_name_new_bg
        )  # target background DB we want to relink to
        relink_exchanges_existing_db(fg_db, db_name_old_bg, new_bg_db)

    else:
        assert (
            db_name_relinked in bw.databases
        ), f"{db_name_relinked} not in databases: {bw.databases}"
        print(f"using existing DB: {db_name_relinked}")


def remove_cols_from_sdf(
    sdf: pd.DataFrame, export_to_excel=False, excel_fp=None
) -> pd.DataFrame:
    """This functions removes some columns in the SDF (scenario difference file), which are unwanted for the input into the LCA-calc objects by the activity-browser.

    Args:
        sdf (pd.DataFrame): scenario difference file (in a pd.DataFrame)
        export_to_excel (bool, optional): _description_. Defaults to False.
        excel_fp (_type_, optional): _description_. Defaults to None.

    Returns:
        pd.DataFrame: _description_
    """

    sdf = sdf[
        sdf.columns.difference(SUPERSTRUCTURE)
    ]  # the columns specified in SUPERSTRUCTURE are removed

    if export_to_excel:
        sdf.to_excel(excel_fp)
        print("export processed SDF file to: {excel_fp}")

    return sdf


def time_stamp(fmt="%Y-%m-%d_%H-%M"):
    """creates a time stamp of now, e.g. "2023-02-15_13-37"

    Args:
        fmt (str, optional): format. Defaults to "%Y-%m-%d_%H-%M".

    Returns:
        str: time stamp, e.g. 2023-02-15_13-37
    """
    return datetime.datetime.now().strftime(fmt)
