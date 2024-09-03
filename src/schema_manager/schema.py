"""Generate and manage schema"""

import os

from google.cloud import bigquery

from config_manager.manager import Params


class SchemaManager:
    """Manage schema to be added to the LLM query"""

    def __init__(self, configs: Params) -> None:
        self.client = bigquery.Client(project=configs.project_id)
        self.table_names = configs.tables
        self.meta_loc = configs.metadata
        self.filter_cols = configs.filter_columns
        self.num_rows = configs.num_rows
        self.schemas = ""

    def read_schema(self) -> None:
        """Read Schemas from txt file"""
        path_ = os.path.join(self.meta_loc, "schemas.txt")
        try:
            with open(path_, "r", encoding="utf-8") as s:
                self.schemas = s.read()
        except FileNotFoundError:
            print("Schema file not found!")
            raise

    def get_n_rows_as_string(self, table: str, cols: list[str], n: int) -> str:
        """Gets a string listing results from n randomly selected rows from the given table"""
        col_names = ", ".join(cols)
        intro_str = f"Sample rows for table: `{table}`:\n\n"
        query_str = f"SELECT {col_names} FROM `{table}` #PARTION_FILTER# ORDER BY RAND() LIMIT {n};"
        query_str = (
            query_str.replace(
                "#PARTION_FILTER#", "WHERE session_date > DATE_TRUNC(CURRENT_DATE(), MONTH)"
            )
            if "onlinebehaviour" in table
            else query_str.replace("#PARTION_FILTER#", "")
        )
        tmp = self.client.query(query_str).result().to_dataframe()
        return intro_str + tmp.to_markdown(index=False) + "\n\n"

    def extract_schemas(self) -> None:
        """Extract schemas of the tables by reading from the tables"""
        self.schemas = ""
        for table in self.table_names:
            table_split = table.split(".")
            querystring = f"""
            SELECT
            column_name, data_type, description
            FROM
            `{".".join(table_split[:-1])}`.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS
            WHERE
            table_name = "{table_split[-1]}";
            """
            self.schemas += f"Schema for table: `{table}`:\n\n"
            tmp = self.client.query(querystring).result().to_dataframe()
            tmp = tmp[~tmp["column_name"].isin(self.filter_cols)].reset_index(drop=True)
            self.schemas += tmp.to_markdown(index=False) + "\n\n"
            self.schemas += self.get_n_rows_as_string(
                table, tmp.column_name.tolist(), self.num_rows
            )

    def get_schemas(self) -> str:
        """Get the schemas for all tables"""
        if not self.schemas:
            try:
                self.read_schema()
            except FileNotFoundError:
                self.extract_schemas()
                self.write_schemas()
        return self.schemas

    def write_schemas(self) -> None:
        """Write shcema to location"""
        path_ = os.path.join(self.meta_loc, "schemas.txt")
        with open(path_, "w", encoding="utf-8") as s:
            s.write(self.schemas)

    def get_dataset_info(self) -> str:
        """Get additional info about dataset"""
        path_ = os.path.join(self.meta_loc, "dataset_info.md")
        contents = ""
        with open(path_, "r", encoding="UTF-8") as f:
            contents = f.read()

        return contents
