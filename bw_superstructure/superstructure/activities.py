# Note: source: functions from AB in activities.py: Lib\site-packages\activity_browser\bwutils\superstructure\activities.py

import brightway2 as bw
from bw2data.backends.peewee import ActivityDataset
import numpy as np
import pandas as pd


FROM_ACT = pd.Index(
    ["from activity name", "from reference product", "from location", "from database"]
)
TO_ACT = pd.Index(
    [
        "to activity name",
        "to reference product",
        "to location",
        "to database",
    ]
)
FROM_BIOS = pd.Index(["from activity name", "from categories", "from database"])
TO_BIOS = pd.Index(["to activity name", "to categories", "to database"])
FROM_ALL = pd.Index(
    [
        "from activity name",
        "from reference product",
        "from location",
        "from categories",
        "from database",
        "from key",
    ]
)
TO_ALL = pd.Index(
    [
        "to activity name",
        "to reference product",
        "to location",
        "to categories",
        "to database",
        "to key",
    ]
)


def process_ad_namedtuple(row) -> tuple:
    """Take a given ActivityDataset namedtuple and return two hashable tuples.

    Allows for matching on name/product/location
    """
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\activities.py
    # branch: activity-browser-dev; version: 2022.11.16

    match = (row.name, row.product, row.location)
    key = (row.database, row.code)
    return match, key


def process_ad_flow(row) -> tuple:
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\activities.py
    # branch: activity-browser-dev; version: 2022.11.16

    match = (row.name, row.data.get("categories", None))
    key = (row.database, row.code)
    return match, key


def get_relevant_flows(df: pd.DataFrame, part: str = "from") -> dict:
    """Determines if all activities from the given 'from' or 'to' chunk"""
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\activities.py
    # branch: activity-browser-dev; version: 2022.11.16

    select = FROM_BIOS if part == "from" else TO_BIOS
    sub = df.loc[:, select]
    sub = sub[sub.iloc[:, 2] == bw.config.biosphere]  # Use only biosphere exchanges
    if sub.empty:
        return {}

    names, categories, dbs = sub.iloc[:, 0:3].apply(set, axis=0)
    query = (
        ActivityDataset.select(
            ActivityDataset.name,
            ActivityDataset.data,
            ActivityDataset.database,
            ActivityDataset.code,
        )
        .where((ActivityDataset.name.in_(names)) & (ActivityDataset.database.in_(dbs)))
        .namedtuples()
    )
    flows = dict(map(process_ad_flow, query.iterator()))
    return flows


def get_relevant_activities(df: pd.DataFrame, part: str = "from") -> dict:
    """Build a dictionary of (name, product, location) -> (database, key) pairs."""
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\activities.py
    # branch: activity-browser-dev; version: 2022.11.16

    select = FROM_ACT if part == "from" else TO_ACT
    sub = df.loc[:, select]
    sub = sub[sub.iloc[:, 3] != bw.config.biosphere]  # Exclude biosphere exchanges
    if sub.empty:
        return {}

    names, products, locations, dbs = sub.iloc[:, 0:4].apply(set, axis=0)
    query = (
        ActivityDataset.select(
            ActivityDataset.name,
            ActivityDataset.product,
            ActivityDataset.location,
            ActivityDataset.database,
            ActivityDataset.code,
        )
        .where(
            (ActivityDataset.name.in_(names))
            & (ActivityDataset.product.in_(products))
            & (ActivityDataset.location.in_(locations))
            & (ActivityDataset.database.in_(dbs))
        )
        .namedtuples()
    )
    activities = dict(map(process_ad_namedtuple, query.iterator()))
    return activities


def match_fields_for_key(df: pd.DataFrame, matchbook: dict) -> pd.Series:
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\activities.py
    # branch: activity-browser-dev; version: 2022.11.16

    def build_match(row):
        if row.iat[4] == bw.config.biosphere:
            match = (row.iat[0], row.iat[3])
        else:
            match = (row.iat[0], row.iat[1], row.iat[2])
        return matchbook.get(match, np.NaN)

    return df.apply(build_match, axis=1)


def fill_df_keys_with_fields(df: pd.DataFrame) -> pd.DataFrame:
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\activities.py
    # branch: activity-browser-dev; version: 2022.11.16

    matches = get_relevant_flows(df, "from")
    matches.update(get_relevant_activities(df, "from"))
    df["from key"] = match_fields_for_key(df.loc[:, FROM_ALL], matches)
    matches = get_relevant_flows(df, "to")
    matches.update(get_relevant_activities(df, "to"))
    df["to key"] = match_fields_for_key(df.loc[:, TO_ALL], matches)
    return df
