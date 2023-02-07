import pathlib as pt
import brightway2 as bw

from .adapted.controllers_database import (
    relink_database,
)
from .lcacalculation import (
    get_scenario_difference_dataframe,
    calculate_lca_results,
    export_lca_scores,
)

from .bw import get_functional_units, get_lcia_methods


def relink_database_to_new_background(
    db_name,
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

        relink_database(db_name_relinked, db_name_old_bg, db_name_new_bg)

    else:
        assert (
            db_name_relinked in bw.databases
        ), f"{db_name_relinked} not in databases: {bw.databases}"
        print(f"using existing DB: {db_name_relinked}")


def create_calculation_setup(
    db_name,
    calc_setup_name: str,
    fp_functional_units: pt.Path,
    fp_lcia_methods: pt.Path,
    db_name_new_bg: str,
    db_name_ecoinvent="ecoinvent38_cutoff",
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


def calculate_scenario_LCA(
    calc_setup_name: str,
    path_to_SDF: pt.Path,
    sdf_sheet_idx=0,
    export_results_to_excel=True,
    fp_export_lca_results=pt.Path("./exports"),
):

    scenario_diff_file = get_scenario_difference_dataframe(
        path_to_SDF, sheet_idx=sdf_sheet_idx
    )
    mlca, contributions, mc = calculate_lca_results(calc_setup_name, scenario_diff_file)

    if export_results_to_excel:
        export_lca_scores(mlca, fp_export_lca_results)

    return mlca, contributions, mc
