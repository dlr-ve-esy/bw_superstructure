﻿# Note: source: activity-browser: functions from: Lib\site-packages\activity_browser\bwutils\strategies.py

import brightway2 as bw
import warnings
from bw2io import activity_hash
from bw2io.utils import DEFAULT_FIELDS
from bw2io.errors import StrategyError
from bw2io.strategies.generic import format_nonunique_key_error
from bw2data.errors import ValidityError
from bw2data.backends.peewee import sqlite3_lci_db


def relink_exchanges_existing_db(db: bw.Database, old: str, other: bw.Database) -> None:
    """Relink exchanges after the database has been created/written.

    This means possibly doing a lot of sqlite update calls.
    """

    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\strategies.py
    # branch: activity-browser-dev; version: 2022.11.16
    # modified by DLR: added 1 IOError and 1 warning statement about altered

    # db = FG-db to be relinked
    # old = old-BG DB, eg ecoinvent
    # other = new-BG DB, e.g. SS from premise

    # IOError added by DLR, we need to check, whether the DB "other" exists in the project. Otherwise we cannot relink to it.
    if other.name not in bw.databases:
        raise IOError(
            f'The selected new background database "{other.name}" is not existing in your project. Therefore, we cannot relink to it. Existing DBs are: \n {list(bw.databases)}'
        )

    if old == other.name:
        print("No point relinking to same database.")
        return
    assert db.backend == "sqlite", "Relinking only allowed for SQLITE backends"
    assert other.backend == "sqlite", "Relinking only allowed for SQLITE backends"

    duplicates, candidates = {}, {}
    altered = 0

    for ds in other:
        key = activity_hash(ds, DEFAULT_FIELDS)
        if key in candidates:
            duplicates.setdefault(key, []).append(ds)
        else:
            candidates[key] = ds.key

    with sqlite3_lci_db.transaction() as transaction:
        try:
            # Only do relinking on external biosphere/technosphere exchanges.
            for i, exc in enumerate(
                exc
                for act in db
                for exc in act.exchanges()
                if exc.get("type") in {"biosphere", "technosphere"}
                and exc.input[0] == old
            ):
                # Use the input activity to generate the hash.
                key = activity_hash(exc.input, DEFAULT_FIELDS)
                if key in duplicates:
                    raise StrategyError(
                        format_nonunique_key_error(
                            exc.input, DEFAULT_FIELDS, duplicates[key]
                        )
                    )
                elif key in candidates:
                    exc["input"] = candidates[key]
                    altered += 1
                exc.save()
                if i % 10000 == 0:
                    # Commit changes every 10k exchanges.
                    transaction.commit()
        except (StrategyError, ValidityError) as e:
            print(e)
            transaction.rollback()
    # Process the database after the transaction is complete.
    #  this updates the 'depends' in metadata

    # warning added by DLR
    if altered == 0:
        # del bw.databases[db.name]  # we delete the db again, since it would be empty

        warnings.warn(
            f'\n \n --- WARNING --- : \n For DB "{db.name}": 0 exchanges could be relinked from original background database "{old}" to new background database "{other.name}".'
            f"If the new Database is a superstructure for scenario LCA calculation, your scenario LCA calculation may fail."
            f'Please, check your databases. The new database "{other.name}" might be empty. \n \n'
            f'If you set "create_new_db_relinked"=False, this warning might be less relevant, since your already existing DB might have already been relinked and thus does not require additional relinking. \n '
        )

    db.process()
    print(
        "Relinked database '{}', {} exchange inputs changed from '{}' to '{}'.".format(
            db.name, altered, old, other.name
        )
    )
