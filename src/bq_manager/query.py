"""Manage BigQuery executiona and authentication"""

import pandas as pd
from google.cloud import bigquery
from ydata_profiling import ProfileReport

from config_manager.manager import Params


class BQManager:
    """Manage BigQuery"""

    def __init__(self, configs: Params) -> None:
        self.bq_client = bigquery.Client(project=configs.project_id)
        self.filter_cols = configs.filter_columns

    def execute_sql(self, query: str) -> pd.DataFrame:
        """Execute SQL query in Bigquery"""
        if not query:
            return pd.DataFrame()
        try:
            ans = self.bq_client.query(query.strip()).result().to_dataframe()
        except Exception as exc:  # pylint: disable=broad-except
            ans = pd.DataFrame(data={"Error": exc}, index=[0])
        return ans

    def data_profiling(self, table_name: str) -> str:
        """Run data profiling tool"""
        table_split = table_name.split(".")
        col_query = f"""
        SELECT column_name
        FROM `{".".join(table_split[:-1])}`.INFORMATION_SCHEMA.COLUMNS
        WHERE table_name = "{table_split[-1]}"
        """
        col_names = self.bq_client.query(col_query).result().to_dataframe()
        tmp = col_names[~col_names["column_name"].isin(self.filter_cols)].column_name.tolist()
        tmp = [x for x in tmp if "date" not in x]
        col_names = ", ".join(tmp)

        query = f"""
        SELECT  {col_names}
        FROM  `{table_name}`
        LIMIT  50000
        """
        res = self.bq_client.query(query).result().to_dataframe()
        profile = ProfileReport(res)
        return profile.to_html()
