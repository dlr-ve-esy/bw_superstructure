# Note: source: activity-browser: functions from: Lib\site-packages\activity_browser\bwutils\commontasks.py

import brightway2 as bw


def count_database_records(name: str) -> int:
    """To account for possible brightway database types that do not implement
    the __len__ method.
    """
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\commontasks.py
    # branch: activity-browser-dev; version: 2022.11.16

    db = bw.Database(name)
    try:
        return len(db)
    except TypeError as e:
        print("{}. Counting manually".format(e))
        return sum(1 for _ in db)


# Formatting
def wrap_text(string: str, max_length: int = 80) -> str:
    """Wrap the label making sure that key and name are in 2 rows.

    idea from https://stackoverflow.com/a/39134215/4929813
    """

    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\commontasks.py
    # branch: activity-browser-dev; version: 2022.11.16
    # adaptations: fold unactivated

    def fold(line: str) -> str:
        return line
        # return textwrap.fill(
        #     line, width=max_length, break_long_words=True, replace_whitespace=False
        # )  # TODO: delete this function later in the other functions, since not needed for us probably (just for GUI)

    return "\n".join(map(fold, string.splitlines()))


def format_activity_label(key, style="pnl", max_length=40):
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\commontasks.py
    # branch: activity-browser-dev; version: 2022.11.16

    try:
        act = bw.get_activity(key)

        if style == "pnl":
            label = "\n".join(
                [
                    act.get("reference product", ""),
                    act.get("name", ""),
                    str(act.get("location", "")),
                ]
            )
        elif style == "pnl_":
            label = " | ".join(
                [
                    act.get("reference product", ""),
                    act.get("name", ""),
                    str(act.get("location", "")),
                ]
            )
        elif style == "pnld":
            label = " | ".join(
                [
                    act.get("reference product", ""),
                    act.get("name", ""),
                    str(act.get("location", "")),
                    act.get("database", ""),
                ]
            )
        elif style == "pl":
            label = ", ".join(
                [
                    act.get("reference product", "") or act.get("name", ""),
                    str(act.get("location", "")),
                ]
            )
        elif style == "key":
            label = str(act.key)  # safer to use key, code does not always exist

        elif style == "bio":
            label = ",\n".join([act.get("name", ""), str(act.get("categories", ""))])
        else:
            label = "\n".join(
                [
                    act.get("reference product", ""),
                    act.get("name", ""),
                    str(act.get("location", "")),
                ]
            )
    except:
        if isinstance(key, tuple):
            return wrap_text(str("".join(key)))
        else:
            return wrap_text(str(key))
    return wrap_text(label, max_length=max_length)
