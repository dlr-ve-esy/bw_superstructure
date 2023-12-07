import pandas as pd
import pathlib as pt

from typing import Dict, Union
from collections import namedtuple
from ruamel.yaml import YAML

import brightway2 as bw


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
    fp_functional_units: pt.Path = None,
    functional_units_sheet: Union[str, int] = 0,
    additional_functional_units: list[tuple[str]] = None,
) -> list:
    """Gets the functional units which can be read in either via the fp_functional_units or via additional_functional_units, or from both arguments at the same time.

    Args:
        fp_functional_units (pt.Path, optional): filepath to an excel file containing the functional units with the headers ['product', 'process', 'location', 'database']. Defaults to None.
        functional_units_sheet (str, int, optional): string or position index for the excel sheet to use in the excel file specified in fp_functional_units
        additional_functional_units (list[tuple[str]], optional): Lists additional functional units in the form of tuples. Each tuple contains the strings for product, process, location, database. Defaults to None.

    Returns:
        list: all functional units in the excel file from fp_functional_units or in the list of tuples for additional_functional_units
    """

    if fp_functional_units is None and additional_functional_units is None:
        print(
            f"ERROR: No functional units are provided by the user. Both 'fp_functional_units' and 'additional_functional_units' are 'None'. Please specify functional units via one or both of the two options."
        )
        exit(78)

    functional_units = []

    additional_functional_units = (
        [] if additional_functional_units is None else additional_functional_units
    )
    additional_functional_units = pd.DataFrame(
        additional_functional_units,
        columns=["product", "process", "location", "database"],
    )

    fu_input = []

    if fp_functional_units:
        fu_input = pd.read_excel(
            fp_functional_units, header=0, sheet_name=functional_units_sheet
        )
        fu_input.dropna(axis="index", how="all", inplace=True)
        print(f'Imported functional units from the file: "{fp_functional_units}"')

    else:
        fu_input = pd.DataFrame(
            fu_input, columns=["product", "process", "location", "database"]
        )

    fu_input = pd.merge(
        fu_input,
        additional_functional_units,
        how="outer",
        on=["process", "product", "location", "database"],
    )

    assert (
        len(fu_input) > 0
    ), f"no functional units could be read in. \n The filepath to functional units is: {fp_functional_units} \n The additional functional units are: {additional_functional_units}"

    selected_dbs = list(fu_input["database"].unique())
    print("DBs of functional units:", selected_dbs)

    available_dbs = list(bw.databases)

    unavailable_dbs = [idb for idb in selected_dbs if idb not in available_dbs]
    assert (
        not unavailable_dbs
    ), f"the following database names in the functional units from the excel sheet are not in the project: {unavailable_dbs} \n DBs in the project are: {available_dbs}"

    has_errors = False
    no_location = False
    no_reference_product = False

    for (
        idx,
        irow,
    ) in fu_input.iterrows():
        # TODO: could be optimized by first grouping the df by db-name and then loop over these groups, to avoid changing dbs repeatedly

        idb_name = irow["database"]
        iproduct = irow["product"]
        iprocess = irow["process"]
        iloc = irow["location"]

        acts = bw.Database(idb_name).search(
            iprocess,
        )  # Note: the filter of the .search() function is a bit buggy for locations and products, therefore we do not use it here.
        # search only does partial matches (searches for sub-strings)

        if len(acts) == 0:
            print(
                f"ERROR: Could not find any activity for the given functional unit: \n  product={iproduct}, \n  process={iprocess}, \n  loc={iloc} \n  in database '{idb_name}'"
            )
            has_errors = True
            continue

        # filter for correct location and reference product
        acts_subset = [
            iact
            for iact in acts
            if (
                iact["location"] == iloc
                and iact["reference product"] == iproduct
                and iact["name"] == iprocess
            )
        ]  # ensure exact match of process name (search above does only partial matches (sub-strings))

        if len(acts_subset) == 0:
            no_location = True
            no_reference_product = True
            locs = set()
            ref_prods = set()

            for iact in acts:
                locs.add(iact["location"])
                ref_prods.add(iact["reference product"])
                if no_location and iact["location"] == iloc:
                    no_location = False
                if no_reference_product and iact["reference product"] == iproduct:
                    no_reference_product = False

        if no_location or no_reference_product:
            has_errors = True
            print(
                "ERROR: found no activity for the given information: \n  product={iproduct}, \n  process={iprocess}, \n  loc={iloc} \n  in database '{idb_name}'"
            )
        if no_location:
            print(
                f'ERROR: requested location "{iloc}" not found. Available locations are: \n{locs}'
            )
        if no_reference_product:
            print(
                f'ERROR: requested reference product "{iproduct}" not found. Available reference products are: \n{ref_prods}'
            )

        if len(acts_subset) > 1:
            print(
                f"ERROR: found {len(acts_subset)} activities for bw2_activity product={iproduct}, process={iprocess}, location={iloc}, in {idb_name} instead of 1 bw2_activity. \n The activities found are: \n {acts_subset}"
            )
            continue

        acts_subset = acts_subset[0]

        functional_units.append(acts_subset)

    if has_errors:
        exit(78)

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
            get_bw2_lcia_method(imeth[0], imeth[1], imeth[2]),  # real bw2-object
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
    # print(f"selected LCIA method: {lcia_method}")

    return lcia_method


def create_calculation_setup(
    calc_setup_name: str,
    fp_lcia_methods: pt.Path,
    fp_functional_units: pt.Path = None,
    functional_units_sheet: Union[str, int] = 0,
    additional_functional_units: list[tuple[str]] = None,
):
    """creates a calculation setup using brightway2. Functional units can be read in either via the fp_functional_units or via additional_functional_units, or from both arguments at the same time.

    Args:
        calc_setup_name (str): name of the calculation setup.
        lcia_methods (pt.Path): path to a yaml file providing lcia methods
        fp_functional_units (pt.Path, optional): filepath to an excel file containing the functional units with the headers ['product', 'process', 'location', 'database']. Defaults to None.
        additional_functional_units (list[tuple[str]], optional): Lists additional functional units in the form of tuples. Each tuple contains the strings for product, process, location, database. Defaults to None.
    """

    if additional_functional_units:
        assert (
            len(additional_functional_units[0]) == 4
        ), "the provided additional functional units do not have enough fields.\n Please provide a list of tuples with each tuple containing in the given order the information: \n product, process, location and database."

    functional_units = get_functional_units(
        fp_functional_units,
        functional_units_sheet,
        additional_functional_units=additional_functional_units,
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
        f"\n Created calculation setup: {calc_setup_name} \n {len(functional_units)} functional units: \n {[ifu for ifu in functional_units]} \n \n {len(lcia_methods)} LCIA Methods: \n {[imeth.internal_name for imeth in lcia_methods.values()]}"
    )  # TODO: improve print of FUs
