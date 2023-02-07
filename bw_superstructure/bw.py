from collections import namedtuple
import pathlib as pt
from ruamel.yaml import YAML
from typing import Dict
import brightway2 as bw

import pandas as pd


pd.set_option("display.max_columns", None)


MethodTuple = namedtuple(
    "MethodTuple",
    [
        "family",  # official BW2-string
        "impact_category",  # official BW2-string
        "details",  # official BW2-string
        "internal_name",  # own name, free to choose
        "internal_abbreviation",  # own name, free to choose
        "bw2_object",  # real bw2-object
    ],
)


def get_functional_units(
    db_name,
    fp_functional_units: pt.Path,
    db_name_new_bg=None,  # : str,
    db_name_ecoinvent=None,  # : str,
):

    functional_units = []
    allowed_db_names = [
        "fritsb_relinked",
        "ecoinvent_in_superstructure",
        "ecoinvent",
    ]  # FIXME: allowed db names do not apply here
    # so far these two db-names are allowed in the excel file
    # fritsb_relinked = exported DB by fritsb and relinked to superstructure
    # ecoinvent_in_superstructure = if process is an ecoinvent process and should be taken from the superstructure
    # ecoinvent = if process is in original ecoinvent, assuming this is called "ecoinvent38_cutoff"  # TODO: this could be done more explicitly

    fu_input = pd.read_excel(fp_functional_units, header=0)
    fu_input = fu_input.fillna("")

    relevant_databases = list(fu_input["database"].unique())
    print("relevant DBs:", relevant_databases)

    assert all(
        idb in allowed_db_names for idb in relevant_databases
    ), f"there are database names in the excel sheet which are not allowed. Allowed names are: {allowed_db_names}"

    db_out_relinked = (
        bw.Database(db_name + "_relinked")
        if "fritsb_relinked" in relevant_databases
        else None
    )

    db_new_bg = (
        bw.Database(db_name_new_bg)
        if "ecoinvent_in_superstructure" in relevant_databases
        else None
    )

    db_ecoinvent = (
        bw.Database(db_name_ecoinvent) if "ecoinvent" in relevant_databases else None
    )

    for idx, irow in fu_input.iterrows():
        idb = irow["database"]
        iproduct = irow["product"]
        iprocess = (
            "operation only - " + irow["process"]
            if idb == "fritsb_relinked"
            else irow["process"]
        )
        iloc = irow["location"]

        if idb == "fritsb_relinked":
            acts = db_out_relinked.search(
                iprocess,  # process name
                filter={
                    "location": iloc,
                },
            )  # requires at least 1 string, cannot combine the str + keyword in filter

            # ensure exact match of c_name and c_product, since search above does only partial matches (sub-strings)

        elif idb == "ecoinvent_in_superstructure":
            acts = db_new_bg.search(
                iprocess,  # process name
                filter={
                    "location": iloc,
                },
            )

        elif idb == "ecoinvent":
            acts = db_ecoinvent.search(
                iprocess,  # process name
                filter={
                    "location": iloc,
                },
            )

        acts = [
            iact
            for iact in acts
            if (iact["name"] == iprocess and iact["reference product"] == iproduct)
        ]  # note: check with process name is also needed, since search does not compare strings whether they are equal, but whether they are contained

        assert (
            len(acts) == 1
        ), f"found {len(acts)} activities for bw2_activity {iproduct, iprocess, iloc, idb} instead of 1 bw2_activity. \n The activities found are: \n {acts}"

        acts = acts[0]

        functional_units.append(acts)

    print(f"selected functional units:{functional_units}")

    return functional_units


def get_lcia_methods(fp: pt.Path) -> Dict[str, MethodTuple]:

    if not fp.exists():
        raise IOError(f'specified file for lcia methods not found at "{fp.absolute()}"')

    inputdata = YAML(typ="safe").load(fp)

    lcia_methods = {}

    for imeth in inputdata.values():  # loop over the list of input from yaml file

        lcia_methods[imeth[3]] = MethodTuple(
            imeth[0],  # official BW2-string
            imeth[1],  # official BW2-string
            imeth[2],  # official BW2-string
            imeth[3],  # own name, free to choose
            imeth[4],  # own abbreviation, free to choose
            get_bw2_lcia_method(
                imeth[0], imeth[1], imeth[2]
            ),  # real bw2-object  # TODO refactor function to get_bw2_method()
        )

    print(
        f"selected {len(lcia_methods)} LCIA methods: {[(imeth.internal_name, imeth.bw2_object) for imeth in lcia_methods.values()]}"
    )

    return lcia_methods


def get_bw2_lcia_method(
    meth_s0="IPCC 2013",
    meth_s1="climate change",
    meth_s2="GWP 100a",
):
    """gets the lcia method from BW

    Args:
        meth_s0 (str, optional): family. Defaults to "IPCC 2013".
        meth_s1 (str, optional): impact category. Defaults to "climate change".
        meth_s2 (str, optional): time horizon. Defaults to "GWP 100a".

    Returns:
        tuple(str, str, str): lcia method, e.g. ("IPCC 2013", "climate change", "GWP 100a")
    """

    # get "IPCC 2013, climate change, GWP 100a"

    lcia_method = []

    for imeth in bw.methods:
        if meth_s0 == imeth[0] and meth_s1 == imeth[1] and meth_s2 == imeth[2]:
            lcia_method.append(imeth)

    assert (
        len(lcia_method) == 1
    ), f"myMethod does not have correct length. We found {len(lcia_method)} methods instead of 1"

    lcia_method = lcia_method[0]
    print(f"selected LCIA method: {lcia_method}")

    return lcia_method
