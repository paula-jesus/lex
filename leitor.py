import os
import pandas as pd
from io import StringIO
import looker_sdk
import streamlit as st

class DataReader:
    """
    This class is responsible for reading SQL files and executing them on a Redshift database.

    Attributes:
        model_name (str): The name of the model.
        file_dir (str): The directory of the file.
    """
    def __init__(self):
        """
        The constructor for DataReader class.

        Attributes:
            model_name (str): The name of the model.
            file_dir (str): The directory of the file.
        """
        self.model_name = "prod-redshift"
        self.file_dir = os.path.dirname(__file__)

    def read_sql(self, folder, file_name):
        """
        This method reads an SQL file and executes it on a Looker instance.

        It sets up the Looker SDK environment variables, reads the SQL file, initializes the Looker SDK,
        creates an SQL query using the Looker SDK, runs the query, and returns the results as a pandas DataFrame.

        Args:
            folder (str): The folder where the SQL file is located.
            file_name (str): The name of the SQL file.

        Returns:
            DataFrame: A pandas DataFrame containing the results of the SQL query.
        """
        os.environ["LOOKERSDK_BASE_URL"] = 'https://loggi.looker.com:19999'
        os.environ["LOOKERSDK_API_VERSION"] = "4.0"
        os.environ["LOOKERSDK_VERIFY_SSL"] = "true"
        os.environ["LOOKERSDK_TIMEOUT"] = "600"
        os.environ["LOOKERSDK_CLIENT_ID"] =  st.secrets["LOOKER_CLIENT_ID"]
        os.environ["LOOKERSDK_CLIENT_SECRET"] = st.secrets["LOOKER_CLIENT_SECRET"]
        file_path = os.path.join(self.file_dir, folder, file_name)
        with open(file_path, 'r') as sql_file:
            sql_query = sql_file.read()
        sdk = looker_sdk.init40()
        slug = sdk.create_sql_query(body=looker_sdk.models40.SqlQueryCreate(connection_name=self.model_name, sql=sql_query)).slug
        response = sdk.run_sql_query(slug=slug, result_format='csv')
        data = pd.read_csv(StringIO(response))
        return data
