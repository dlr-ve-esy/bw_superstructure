import pandas as pd
import brightway2 as bw
from bw_superstructure.superstructure.utils import SUPERSTRUCTURE
from bw_superstructure.superstructure.activities import (
    fill_df_keys_with_fields,
)
from bw_superstructure.superstructure.utils import guess_flow_type

# Note: source: based on: activity-browser: methods from class SuperstructureManager(object)
# (Lib\site-packages\activity_browser\bwutils\superstructure\manager.py)
# branch: activity-browser-dev; version: 2022.11.16
# adaptations: extracted the methods of the class SuperstructureManager(object) as stand-alone functions

EXCHANGE_KEYS = pd.Index(["from key", "to key"])
INDEX_KEYS = pd.Index(["from key", "to key", "flow type"])


def format_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Format the input superstructure dataframes.
    If in the future more formatting functions are needed, they should be added here.
    """
    # Note: source: based on: activity-browser: method from class SuperstructureManager(object)
    # (Lib\site-packages\activity_browser\bwutils\superstructure\manager.py)
    # branch: activity-browser-dev; version: 2022.11.16
    # adaptations: extracted method as stand-alone function

    if not isinstance(df.index, pd.MultiIndex):
        df.index = build_index(df)
    df = remove_duplicates(df)
    df = merge_flows_to_self(df)

    return df


def merge_flows_to_self(df: pd.DataFrame) -> pd.DataFrame:
    """Merge any 'technosphere' flows to and from the same key (a.k.a. flow to self).

    This function checks if any flows to self exist and merges them with a production flow.
    If no production flow exists, it is added.
    """
    # Note: source: based on: activity-browser: method from class SuperstructureManager(object)
    # (Lib\site-packages\activity_browser\bwutils\superstructure\manager.py)
    # branch: activity-browser-dev; version: 2022.11.16
    # adaptations: extracted method as stand-alone function

    # get all flows to self
    flows_to_self = df.loc[
        df.apply(
            lambda x: True
            if x["from key"] == x["to key"] and x["flow type"] == "technosphere"
            else False,
            axis=1,
        ),
        :,
    ]

    if len(flows_to_self) > 0:
        for idx in flows_to_self.index:
            prod_idx = (idx[0], idx[1], "production")
            tech_idx = (idx[0], idx[1], "technosphere")
            scenario_cols = df.columns.difference(SUPERSTRUCTURE)
            if not df.index.isin([prod_idx]).any():
                # this flow to self does not have a similar 'production' flow to self.
                # find the default production value and add it as a 'production' flow

                # WARNING: this way of getting the production amount only works for processes with
                # 1 reference flow (because we just take index 0 from list of production exchanges)
                # Once AB has support for multiple reference flows, we need to adjust this code to match the
                # right flow -something with looping over the flows and getting the right product or something-.
                prod_amt = list(bw.get_activity(idx[0]).production())[0].get(
                    "amount", 1
                )

                # make a new df to edit the production, add the correct values/indices where needed
                # and concat to the main df
                new_prod = pd.DataFrame(df.loc[tech_idx, :])
                new_prod.loc[tech_idx, "flow type"] = "production"
                new_prod.loc[tech_idx, scenario_cols] = prod_amt
                new_prod.index = [prod_idx]
                df = pd.concat([df, new_prod], axis=0)

            # subtract the 'technosphere' value from 'production' value and write to 'production'
            prod = df.loc[prod_idx, scenario_cols]
            tech = df.loc[tech_idx, scenario_cols]
            vals = prod.values - tech.values

            # write the corrected values to the right cells
            # TODO figure out how to easily write 'per row' instead of 'per cell', but the below loop works for now
            for i, elem in enumerate(vals.T):
                df.loc[prod_idx, scenario_cols[i]] = elem[0]
        # drop the 'technosphere' flows
        df.drop(flows_to_self.index, inplace=True)
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Using the input/output index for a superstructure, drop duplicates
    where the last instance survives.
    """
    # Note: source: based on: activity-browser: method from class SuperstructureManager(object)
    # (Lib\site-packages\activity_browser\bwutils\superstructure\manager.py)
    # branch: activity-browser-dev; version: 2022.11.16
    # adaptations: extracted method as stand-alone function

    duplicates = df.index.duplicated(keep="last")
    if duplicates.any():
        print("Found and dropped {} duplicate exchanges.".format(duplicates.sum()))
        return df.loc[~duplicates, :]
    return df


def build_index(df: pd.DataFrame) -> pd.MultiIndex:
    """Construct MultiIndex from exchange keys and flows, allowing for
    data merging.

    - If any of the exchange key columns are missing keys, attempt to fill
    them. If filling them does not succeed, raise an assertion.
    """
    # Note: source: based on: activity-browser: method from class SuperstructureManager(object)
    # (Lib\site-packages\activity_browser\bwutils\superstructure\manager.py)
    # branch: activity-browser-dev; version: 2022.11.16
    # adaptations: extracted method as stand-alone function

    if df.loc[:, EXCHANGE_KEYS].isna().any().all():
        df = fill_df_keys_with_fields(df)
        _df = df.loc[:, EXCHANGE_KEYS].notna()
        assert (
            _df.all().all()
        ), "Cannot find all keys. {} of {} exchanges are broken.".format(
            len(df[_df]), len(df)
        )
    unknown_flows = df.loc[:, "flow type"].isna()
    if unknown_flows.any():
        print(
            "Not all flow types are known, guessing {} flows".format(
                unknown_flows.sum()
            )
        )
        df.loc[unknown_flows, "flow type"] = df.loc[unknown_flows, EXCHANGE_KEYS].apply(
            guess_flow_type, axis=1
        )
    return pd.MultiIndex.from_tuples(
        df.loc[:, INDEX_KEYS].apply(tuple, axis=1), names=["input", "output", "flow"]
    )
