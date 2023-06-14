import pandas as pd

from bw_superstructure.superstructure.excel import import_from_excel
from bw_superstructure.superstructure.dataframe import scenario_names_from_df
import bw_superstructure.superstructure.manager as manager

class ScenarioImporter():
	"""Code based on AB ScenarioImportPanel and ScenarioImportWidget
	"""
	def __init__(self):
		self.tables = []

	def scenario_names(self, idx: int) -> list:
		if idx > len(self.tables):
			return []
		return scenario_names_from_df(self.tables[idx])

	def check_duplicates(self, data: pd.DataFrame, index: list=['to key', 'from key', 'flow type']) -> pd.DataFrame:
		"""Code based on ABFileImporter
		Checks three fields to identify whether a scenario difference file contains duplicate exchanges.
		"""
		duplicates = data.duplicated(index, keep=False)
		if duplicates.any():
			print("Duplicates have been found in the provided file. Duplicate entries are discarded, only the last found instance will be used.")
			return data.drop_duplicates(index, keep='last', inplace=False)
		return data

	def clear_tables(self):
		self.tables = []

	def load_scenarios(self, scenario_files, kind):
		for file, sheet_id in scenario_files:
			self.tables.append(import_from_excel(file, sheet_id))
		data = [df for df in self.tables if not df.empty]
		if not data:
			return pd.DataFrame()

		self.scenario_df = manager.combined_data(data, kind, self.check_duplicates)
