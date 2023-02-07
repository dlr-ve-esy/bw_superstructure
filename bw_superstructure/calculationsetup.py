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
    fp_functional_units: pt.Path,
):

    functional_units = []

    fu_input = pd.read_excel(fp_functional_units, header=0)
    fu_input = fu_input.fillna("")

    selected_dbs = list(fu_input["database"].unique())
    print("DBs of functional units:", selected_dbs)

    available_dbs = list(bw.databases)

    unavailable_dbs = [idb for idb in selected_dbs if idb not in available_dbs]
    assert (
        not unavailable_dbs
    ), f"the following database names in the functional units from the excel sheet are not in the project: {unavailable_dbs} \n DBs in the project are: {available_dbs}"

    for (
        idx,
        irow,
    ) in fu_input.iterrows():
        # TODO: could be optimized by first grouping the df by db-name and then loop over these groups, to avoid changing dbs repeatedly

        idb_name = irow["database"]
        iproduct = irow["product"]
        iprocess = (
            "operation only - " + irow["process"]
            if idb_name == "fritsb_relinked"
            else irow["process"]
        )
        iloc = irow["location"]

        acts = bw.Database(idb_name).search(
            iprocess,  # process name
            filter={
                "location": iloc,
            },
        )  # requires at least 1 string, cannot combine the str + keyword in filter

        # ensure exact match of c_name and c_product, since search above does only partial matches (sub-strings)
        acts = [
            iact
            for iact in acts
            if (iact["name"] == iprocess and iact["reference product"] == iproduct)
        ]  # note: check with process name is also needed, since search does not compare strings whether they are equal, but whether they are contained

        assert (
            len(acts) == 1
        ), f"found {len(acts)} activities for bw2_activity {iproduct, iprocess, iloc, idb_name} instead of 1 bw2_activity. \n The activities found are: \n {acts}"

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


def create_calculation_setup(
    calc_setup_name: str,
    fp_functional_units: pt.Path,
    fp_lcia_methods: pt.Path,
):
    """creates a calculation setup using brightway2.

    Args:
        calc_setup_name (str): _description_
        functional_units (List): List of bw2-activity objects.
        lcia_methods (dict): dict with key = str of from MethodTuple.internal_name, value = MethodTuple for that method
    """

    functional_units = get_functional_units(
        fp_functional_units,
    )

    lcia_methods = get_lcia_methods(fp_lcia_methods)

    # simple calc setup
    bw.calculation_setups[calc_setup_name] = {
        "inv": [{(ifu): 1} for ifu in functional_units],
        "ia": [imeth.bw2_object for imeth in lcia_methods.values()],
    }

    # Keys:
    #  `inv`: List of functional units, e.g. ``[{(key): amount}, {(key): amount}]``
    #  `ia`: List of LCIA methods, e.g. ``[(method), (method)]``.
    # note that calculation_setup is just a dict, therefore overwrites if same name is chosen

    print(
        f"calculation setup created: \n name: {calc_setup_name} \n {len(functional_units)} functional units: \n {[ifu for ifu in functional_units]} \n {len(lcia_methods)} LCIA Methods: \n {[imeth.internal_name for imeth in lcia_methods.values()]}"
    )
