import pandas as pd
from .superstructure.utils import SUPERSTRUCTURE


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
