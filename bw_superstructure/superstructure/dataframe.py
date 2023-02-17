﻿# Note: source: functions from AB in dataframe.py: Lib\site-packages\activity_browser\bwutils\superstructure\dataframe.py

import numpy as np
import pandas as pd

from typing import List, Tuple

import brightway2 as bw

from bw_superstructure.bwutils.utils import Index
from bw_superstructure.superstructure.utils import SUPERSTRUCTURE


def arrays_from_indexed_superstructure(
    df: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray]:
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\dataframe.py
    # branch: activity-browser-dev; version: 2022.11.16

    result = np.zeros(df.shape[0], dtype=object)
    for i, data in enumerate(df.index.to_flat_index()):
        result[i] = Index.build_from_dict(
            {"input": data[0], "output": data[1], "flow type": data[2]}
        )
    return result, df.to_numpy(dtype=float)


def filter_databases_indexed_superstructure(
    df: pd.DataFrame, include: set
) -> pd.DataFrame:
    """Filters the given superstructure so that only indexes where the output
    database is in the `include` set are valid.
    """
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\dataframe.py
    # branch: activity-browser-dev; version: 2022.11.16

    return df.loc[[x[1][0] in include for x in df.index.to_flat_index()], :]


def scenario_names_from_df(df: pd.DataFrame) -> List[str]:
    """Returns the list of scenario names from a given superstructure.

    Strip out any possible carriage returns (excel junk)
    """
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\dataframe.py
    # branch: activity-browser-dev; version: 2022.11.16

    cols = scenario_columns(df)
    return [str(x).replace("\n", " ").replace("\r", "") for x in cols]


def superstructure_from_arrays(
    samples: np.ndarray, indices: np.ndarray, names: List[str] = None
) -> pd.DataFrame:
    """Process indices into the superstructure itself, the samples represent
    the scenarios.
    """
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\dataframe.py
    # branch: activity-browser-dev; version: 2022.11.16

    assert samples.ndim == 2, "Samples array should be 2-dimensional"
    assert indices.ndim == 1, "Indices array should be 1-dimensional"
    assert samples.shape[0] == indices.shape[0], "Length mismatch between arrays"
    if names is not None:
        assert (
            len(names) == samples.shape[1]
        ), "Number of names should match number of samples columns"
        names = pd.Index(names)
    else:
        names = pd.Index(["scenario{}".format(i + 1) for i in range(samples.shape[1])])

    # Construct superstructure from indices
    superstructure = pd.DataFrame(map(data_from_index, indices), columns=SUPERSTRUCTURE)
    # Construct scenarios from samples
    scenarios = pd.DataFrame(samples, columns=names)

    df = pd.concat([superstructure, scenarios], axis=1)
    return df


def scenario_columns(df: pd.DataFrame) -> pd.Index:
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\superstructure\dataframe.py
    # branch: activity-browser-dev; version: 2022.11.16

    # 'sort=False' ensures that order of scenario names is not altered.
    return df.columns.difference(SUPERSTRUCTURE, sort=False)
