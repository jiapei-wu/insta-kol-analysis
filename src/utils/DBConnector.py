import os
import subprocess
import yaml
import pandas as pd

from sqlalchemy.engine.create import create_engine
from sqlalchemy.types import Integer, String, DECIMAL, DateTime, VARCHAR
from sqlalchemy import Column, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


import os
import subprocess
import yaml
import pandas as pd

from sqlalchemy.engine.create import create_engine
from sqlalchemy.types import Integer, DateTime
from sqlalchemy import text


class SQLConnect:
    def __init__(
        self,
        dbname=None,
        host=None,
        user=None,
        password=None,
        local_db=False,
        config_path=None,
        **kwargs,
    ):
        """SQL connection helper to simplify the process to send quesries to DB.
            Currently support MySQL and Postgres
            >>> # Use pandas dataframe
            >>> DB_URL = "postgres_url"
            >>> connector = SQLConnect(DB_URL)
            >>> result = connector.executeQuery("select * from accounts;")
            >>> # Use Raw Data
            >>> DB_URL = "postgres_url"
            >>> connector = SQLConnect(DB_URL)
            >>> result = connector.executeQuery("select * from accounts;")
        Args:
            db_url ([type]): [description]
        """
        self.dbname = dbname
        self.host = host
        self.user = user
        self.password = password
        self.local_db = local_db
        self.config_path = config_path
        self.DB_URL = self.get_postgres_url(
            self.dbname,
            self.host,
            self.user,
            self.password,
            self.local_db,
            self.config_path
        )
        self.engine = create_engine(self.DB_URL)

    def get_postgres_url(
        self,
        dbname=None,
        host=None,
        user=None,
        password=None,
        local_db=False,
        config_path=None
    ):

        if dbname and host and user and password and local_db:
            # user = "postgres"
            # password = "123"
            # host = (
            #     "postgres-image-dev"  # or use the container name postgres-env
            # )
            # dbname = "postgres"
            return (
                f"postgresql+psycopg2://{user}:{password}@{host}:5432/{dbname}"
            )
        elif dbname and host and user and password and not local_db and not config_path:
            return f"postgresql+psycopg2://{user}:{password}@{host}:5432/{dbname}?sslmode=require"

        elif config_path and not local_db:

            print("Notice that once config file path is specified, \
                arguments entered manually like dbname, host, user, and password \
                will be ignored")

            with open(config_path) as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                user, password, host, dbname = (
                    config["user"],
                    config["password"],
                    config["host"],
                    config["dbname"]
                )
            return f"postgresql+psycopg2://{user}:{password}@{host}:5432/{dbname}?sslmode=require"

        else:
            raise(
                """
                Please makre sure you:
                    Option 1: Specify the correct dbname, host, user, and password
                    Option 2: Specify the path to your yaml config file path with correct dbname, host, user, and password
                """
            )

    def executeQuery(self, query, to_pandas=True, **kwargs):
        """Execute the query, by default it will return a
        pandas dataframe. If set to_pandas to False then will
        return raw tuple.
        Args:
            query (str): the SQL query
            to_pandas (boo, optional): Defaults to True.
        Returns:
            obj: By default it will return a pandas dataframe.
            If set to_pandas to False then will
            return raw tuple.
        """
        if query.strip().lower().startswith("select"):
            if to_pandas:
                return pd.read_sql(query, self.engine)
            else:
                with self.engine.connect() as connection:
                    result = connection.execute(text(query))
                return result.fetchall()
        else:
            with self.engine.connect() as connection:
                connection.execute(text(query))
            print("table create")

    def insertValue(self, dataframe, insert_format_func=None, bulk_table_format=None, bulk=False):
        """
        Example: 
        INSERT INTO covid19(last_updated_date, location, total_cases)
        VALUES ('{row[0]}', '{row[1]}', {row[2]});
        """
        if not bulk and insert_format_func:
            with self.engine.connect() as conn:
                for idx, row in dataframe.iterrows():
                    q = insert_format_func(row)
                    conn.execute(text(q))
            print("data inserted")
        elif bulk_table_format and bulk and not insert_format_func:
            Session = sessionmaker(self.engine)
            s = Session()
            s.bulk_insert_mappings(
                bulk_table_format,
                dataframe.to_dict(orient="records")
            )
            s.commit()
            print("data inserted")
        else:
            raise("When bulk=TRue, bulk_table_format should be provided")

        

    def viewAllTables(self, view_type="public"):
        """View all existing tables. By default it
        exclude system tables.
        Args:
            view_type (str, optional): Return data tables by type.
                Defaults to "public".
        """
        result = self.executeQuery(
            "SELECT * FROM information_schema.tables;"
        )
        return result[result["table_schema"] == view_type]

