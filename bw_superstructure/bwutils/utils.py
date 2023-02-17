# Note: source: activity-browser: functions from: Lib\site-packages\activity_browser\bwutils\utils.py

from typing import NamedTuple, Optional

from bw2data import config
from bw2data.utils import TYPE_DICTIONARY
from bw2data.backends.peewee import ActivityDataset, ExchangeDataset


class Key(NamedTuple):
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\utils.py
    # branch: activity-browser-dev; version: 2022.11.16

    database: str
    code: str

    @property
    def database_type(self) -> str:
        return "biosphere" if self.database == config.biosphere else "technosphere"


class Index(NamedTuple):
    # Note: source: based on: activity-browser:
    # function from: Lib\site-packages\activity_browser\bwutils\utils.py
    # branch: activity-browser-dev; version: 2022.11.16

    input: Key
    output: Key
    flow_type: Optional[str] = None

    @classmethod
    def build_from_exchange(cls, exc: ExchangeDataset) -> "Index":
        return cls(
            input=Key(exc.input_database, exc.input_code),
            output=Key(exc.output_database, exc.output_code),
            flow_type=exc.type,
        )

    @classmethod
    def build_from_tuple(cls, data: tuple) -> "Index":
        obj = cls(
            input=Key(data[0][0], data[0][1]),
            output=Key(data[1][0], data[1][1]),
        )
        exc_type = ExchangeDataset.get(
            ExchangeDataset.input_code == obj.input.code,
            ExchangeDataset.input_database == obj.input.database,
            ExchangeDataset.output_code == obj.output.code,
            ExchangeDataset.output_database == obj.output.database,
        ).type
        return obj._replace(flow_type=exc_type)

    @classmethod
    def build_from_dict(cls, data: dict) -> "Index":
        in_key = data.get("input", ("", ""))
        out_key = data.get("output", ("", ""))
        return cls(
            input=Key(in_key[0], in_key[1]),
            output=Key(out_key[0], out_key[1]),
            flow_type=data.get("flow type", None),
        )

    @property
    def input_document_id(self) -> int:
        return ActivityDataset.get(
            ActivityDataset.code == self.input.code,
            ActivityDataset.database == self.input.database,
        ).id

    @property
    def output_document_id(self) -> int:
        return ActivityDataset.get(
            ActivityDataset.code == self.output.code,
            ActivityDataset.database == self.output.database,
        ).id

    @property
    def exchange_type(self) -> int:
        if self.flow_type:
            return TYPE_DICTIONARY.get(self.flow_type, -1)
        exc_type = ExchangeDataset.get(
            ExchangeDataset.input_code == self.input.code,
            ExchangeDataset.input_database == self.input.database,
            ExchangeDataset.output_code == self.output.code,
            ExchangeDataset.output_database == self.output.database,
        ).type
        return TYPE_DICTIONARY.get(exc_type, -1)

    @property
    def ids_exc_type(self) -> (int, int, int):
        return self.input_document_id, self.output_document_id, self.exchange_type
