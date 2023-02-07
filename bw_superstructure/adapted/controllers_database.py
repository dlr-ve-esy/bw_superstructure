import brightway2 as bw
from bw_superstructure.bwutils.strategies import (
    relink_exchanges_existing_db,
)


def relink_database(fg_db_name: str, old_bg_db: str, new_bg_db: str):
    """Relink technosphere exchanges within the given database."""

    # Note: source: based on: activity-browser: def relink_database(self, db_name: str);
    # method from class DatabaseController(QObject):
    # in: Lib\site-packages\activity_browser\controllers\database.py
    # branch: activity-browser-dev; version: 2022.11.16
    # adaptation: only took 3 most important functions here

    fg_db = bw.Database(fg_db_name)  # foreground DB
    new_bg_db = bw.Database(new_bg_db)  # target background DB we want to relink to
    relink_exchanges_existing_db(fg_db, old_bg_db, new_bg_db)
