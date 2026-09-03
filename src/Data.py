import pandas as pd
import psycopg2
from psycopg2 import OperationalError

class Data:
    def __init__(self, db: str, user: str, password: str, host: str, port: int):
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def get_connection(self):
        try:
            return psycopg2.connect(
                database=self.db,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
        except OperationalError as e:
            print(f"Connection error: {e}")
            raise

    def fetch_data(self, query):
        try:
            with self.get_connection() as conn:
                return pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"Error fetching data: {e}")
            raise