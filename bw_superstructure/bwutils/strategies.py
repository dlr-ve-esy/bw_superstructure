# Note: source: activity-browser: functions from: Lib\site-packages\activity_browser\bwutils\strategies.py

import brightway2 as bw
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

    # db = FG-db to be relinked
    # old = old-BG DB, eg ecoinvent
    # other = new-BG DB, e.g. SS from premise

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
    db.process()
    print(
        "Relinked database '{}', {} exchange inputs changed from '{}' to '{}'.".format(
            db.name, altered, old, other.name
        )
    )
