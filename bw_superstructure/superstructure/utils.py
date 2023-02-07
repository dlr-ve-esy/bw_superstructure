# Note: source: activity-browser: functions from: Lib\site-packages\activity_browser\bwutils\superstructure\utils.py


import brightway2 as bw
import pandas as pd


# Different kinds of indexes, to allow for quick selection of data from
# the Superstructure DataFrame.
SUPERSTRUCTURE = pd.Index(
    [
        "from activity name",
        "from reference product",
        "from location",
        "from categories",
        "from database",
        "from key",
        "to activity name",
        "to reference product",
        "to location",
        "to categories",
        "to database",
        "to key",
        "flow type",
    ]
)


def guess_flow_type(row: pd.Series) -> str:
    """Given a series of input- and output keys, make a guess on the flow type."""
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\utils.py
    # function: def guess_flow_type(row: pd.Series) -> str:
    # branch: activity-browser-dev; version: 2022.11.16

    if row.iat[0][0] == bw.config.biosphere:
        return "biosphere"
    elif row.iat[0] == row.iat[1]:
        return "production"
    else:
        return "technosphere"
