"""Manage BigQuery executiona and authentication"""

import pandas as pd
from google.cloud import bigquery

from config_manager.manager import Params


class BQManager:  # pylint: disable=too-few-public-methods
    """Manage BigQuery"""

    def __init__(self, configs: Params) -> None:
        self.bq_client = bigquery.Client(project=configs.project_id)
        self.filter_cols = configs.filter_columns

    def execute_sql(self, query_: str) -> pd.DataFrame:
        """Execute SQL query in Bigquery"""
        if not query_:
            return pd.DataFrame()
        try:
            ans = self.bq_client.query(query_.strip()).result().to_dataframe()
            if ans.size == 1:
                ans = ans.astype(str)
        except Exception as exc:  # pylint: disable=broad-except
            ans = pd.DataFrame({"Error": [exc]})
        return ans
