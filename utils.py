import pandas as pd
import streamlit as st
import numpy as np

from estilizador import PageStyler
from leitor import DataReader

import pandas as pd
import gspread
import warnings

warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)

class EstilizarPagina:
    """
    This class is responsible for styling the page.

    Args:
        self (object): Instance of the class.
    """
    def __init__(self):
        self.estilizador = PageStyler()
        self.PAGE_CONFIG = {
            "page_title": "BSC LEX - Loggi",
            "page_icon": "📦",
            "layout": "centered",
        }

    def set_page_config(self):
        """
        This method sets the page configuration and applies general and sidebar CSS.

        Args:
            _self (object): Instance of the class.
        """
        st.set_page_config(**self.PAGE_CONFIG)
        self.estilizador.apply_general_css()
        self.estilizador.apply_sidebar_css()
        st.subheader("BSC LEX - Monitoramento Mensal 📦")

    def display_infos(self): 
        with st.expander("Saiba mais sobre o cálculo dos pesos e frequência de atualização"):
            st.write("""
            **1. Para KPIs em que quanto menor o valor, melhor (por exemplo, OPAV e Absenteísmo):**

            - Se a base alcançar um resultado menor ou igual à meta, será pontuada com o valor integral do peso.

            **2. Para KPIs em que quanto maior o valor, melhor (por exemplo, SLA e Produtividade):**

            - Se a base alcançar um valor maior que a meta, será pontuada com o valor integral do peso.
            - Se a base alcançar um valor menor que a meta, será pontuada de acordo com o cálculo: (resultado atingido / meta) * peso.
                     
            **Frequência de atualização:**
                     
            Dados provenientes do Looker são recarregados quinzenalmente. São eles:

                - SLA, Produtividade, Ocorrências de +2HE, Ocorrências de -11Hs Interjornadas, OPAV, Produtividade Média, SLA, Inventário, Loss Rate.
                
            Dados provenientes de planilhas Google são recarregados diariamente. São eles: 

                - Programa 5S, Auditoria, Auto avaliação, Aderência ao Plano de Capacitação da Qualidade definido para a Base. 

            Exceções: 

                    - Absenteísmo: Todo dia 15 do mês (fonte Looker).
                 - Custo / pacote: Todo dia 18 do mês (fonte planilhas Google).   
                    """)    

class GerarTabelas:
    """
    This class is responsible for generating tables by reading SQL files.

    Args:
        _self (object): Instance of the class. Self with undercore is used to cache the data and avoid conflicts with streamlit. More informations about it here: https://discuss.streamlit.io/t/from-st-cache-to-st-cache-data-in-a-class/37667
    """
    def __init__(_self):
        _self.leitor = DataReader()

    @st.cache_data(show_spinner=False, ttl=840000)
    def gerar_dados(_self, filename):
        """
        This method reads the 'dados_lex.sql' file and returns its content.

        Args:
            filename (str): The name of the SQL file.

        Returns:
            DataFrame: A pandas DataFrame containing the data read from the SQL file.
        """
        return _self.leitor.read_sql("SQL", f"{filename}.sql")


    @st.cache_data(show_spinner=False, ttl=30)
    def gerar_tabela_sheets(worksheet):
        """
        Function to fetch data from a specific Google Sheets document and return it as a pandas DataFrame.

        Args:
            worksheet (str): The name of the worksheet in the Google Sheets document to fetch data from.

        Returns:
            DataFrame: The fetched data as a pandas DataFrame.
        """
        google_sheets_api_credentials = {
        "type": "service_account",
        "project_id": "ba-automatizacoes",
        "private_key_id": "70f3e9d765597458d010a63d0bc66f76a2810881",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDusgUBiH6+v9+y\ncZnQniA3hed4gqmglISH34XoF4De+T5hiE2eNt8wigWqVL3KmPYB9L8vYlx3rfuf\ng+7NttJLmXeQemNeEed4QHNVq/+tT5VWt/2cT2gl8Hw+o5yYqlfcEnmybG4odJ7k\naV7lY9+AklDz5Ia4JZ2q5d6fG4Y0F6xrBTrHNCxloN12COBYZ2aQh5JbnWLyViT5\njBaF4ElaqjNeSrhHJD2Oz/sD2NdybfhXon4Ckw1GHwT4gG6QckN0lOmrS7o64J+K\nDVshBx89ZwMH7xXOFVI4cuVrTTnribifYtQVUgk+ILBOgHqLmK8pcmb4hMk+8Qvg\nJBkyGeYjAgMBAAECggEAZ6UDCXRkXJ1iG9C6Elzm7lUFek16LFDw7zK+qVWzTp55\nWM5frahz51a3OQvM0XDzuUu1zHRwZEM2tEAMbGTLEaqUwTZzeUBa+ts5eWTTA0VA\nOkRwKfRM69RtjqFqeNvWhKe9Eh2FA6oH6HRckUx5mxFtd0muub0TpkZkEUBZWLps\nD8hNtZxx/7+LprALYKmVb2KHSs+fvlPaPgf5eEcPJ26rnUFNzH32XdJk+ve4Ckdh\nvckBBjnXmY91WIyRDdPrxWAdnU/+Uww8JoisSlAvjh2CbxRJNqF4kQoBMIB3A3Yk\nB8rc7pexmkRwFBBrwaVGrBUnAGla1zv2JubwQ0mkuQKBgQD+THWGmL6ffbSq+6US\nTxTXM8L4cnZaQs/BHSblX4kVcvZ7/XIkjA8sqZ/LOpud0S2SBUgl9bXSf1YAq7iD\n2/6IhNnqvRzFc3tw26tJgcCCA6v86OG+4naGZZttKlh/geiwzYHIlkMROmXrkcv9\ng/OAf/NMuVv4Ei9MZ5cRs2tINQKBgQDwStYltk6MEUyqwL3WJPxSvQjpNStv3ttR\nA+my8TSQbME+9Uf+DoN8CjfRK+2la5q81cKcETFFpipDxE/cAHf/eXqKE77Qn5wZ\n8DxQZ9Q7GBgFGXWHZpcA/Eya3/kPQ4nX5gpGtD8RnhwspU+U4LN9+hNUT550tVYZ\nFOIRN6+v9wKBgH+9trfTGMaTZeMSH9yvnv9vf/w/u1YiA6y1USmdsQX2Rv0H1oOn\nW6QK3TtAiJVhU2vrfU+cOyavUmtp13ldVGINok35i29gUFzj7AozxJlK8OVNssCp\nj/J5LfdLc0Mx5cqSoSQ63xvTYwlPptIFq5ccLwKWhi16LQpLaya4IycVAoGBAMXa\nON2wcJhwHhpyvVy383ME53NuLifc7eSVPjXy2X8ZrTxzpiWQOb9GgpMegny0TyKx\nN55doZ5hpWdLGx5g3G1kzvsmKvWIlnXdEyx5cYx+2DhKsDUeybMsCr9zL5Xb3IIC\nje+NtmiBMV2peA9zvRc7c/L149jg/tWEFmhq26QdAoGBAOQ/Kcoo0TEN0Ll2fSeO\nbbsJtADTESijXcC5HcPn5S+LkfWR+1ikLYVW9x9I9JdcxAxPViWKeflXrmW2ATQG\nO9FIL/Mnirw2ljuK+zbV2b9+KQ/p0nelBTGijcX5HXI0SlN3vZv3JG/8JJTwjM/C\nEoWNIbDGLTe7adohlKUo/90F\n-----END PRIVATE KEY-----\n",
        "client_email": "google-sheets-ba@ba-automatizacoes.iam.gserviceaccount.com",
        "client_id": "106532525291839556687",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-ba%40ba-automatizacoes.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
        } 

        gc = gspread.service_account_from_dict(google_sheets_api_credentials)
        sh = gc.open_by_key('1wQs6k5eGKASNxSMYcfHwP5HK7PSEDo0t_uzLYke_u3s')

        ws = sh.worksheet(worksheet)
        data = ws.get_values(value_render_option="UNFORMATTED_VALUE", date_time_render_option="FORMATTED_STRING")

        df = pd.DataFrame(data[1:], columns=data[0])

        return df


class FormatoNumeros:
    def format_rows(df, row_labels, format_func):
        """
        Applies a formatting function to specific rows of a DataFrame.

        Args:
            df (DataFrame): The DataFrame to format.
            row_labels (list): The labels of the rows to format.
            format_func (function): The formatting function to apply.

        Returns:
            DataFrame: The formatted DataFrame.
        """
        df.loc[row_labels] = df.loc[row_labels].apply(format_func, axis=1)
        return df

    def format_func_percent(row):
        """
        Formats a row of a DataFrame as percentages.

        Args:
            row (Series): The row to format.

        Returns:
            Series: The formatted row.
        """
        row.iloc[:-1] = row.iloc[:-1].apply(lambda x: f'{x:.0f}%' if isinstance(x, (int, float)) and np.isfinite(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (int, float)) and np.isfinite(x) else x)
        last_cell = row.iloc[-1]
        row.iloc[-1] = f'{last_cell:.0f}' if isinstance(last_cell, (int, float)) and np.isfinite(last_cell) and last_cell == int(last_cell) else f'{last_cell:.2f}' if isinstance(last_cell, (int, float)) and np.isfinite(last_cell) else last_cell
        return row

    def format_func(row):
        """
        Formats a row of a DataFrame as numbers with two decimal places.

        Args:
            row (Series): The row to format.

        Returns:
            Series: The formatted row.
        """
        return row.apply(lambda x: f'{x:.0f}' if isinstance(x, (int, float)) and np.isfinite(x) and x == int(x) else f'{x:.2f}' if isinstance(x, (int, float)) and np.isfinite(x) else x)
    
    def format_func_finance(row):
        """
        Formats a row of a DataFrame as currency values.

        Args:
            row (Series): The row to format.

        Returns:
            Series: The formatted row.
        """
        row.iloc[:-1] = row.iloc[:-1].apply(lambda x: f'R$ {x:.0f}' if isinstance(x, (int, float)) and np.isfinite(x) and x == int(x) else f'R$ {x:.2f}' if isinstance(x, (int, float)) and np.isfinite(x) else x)
        last_cell = row.iloc[-1]
        row.iloc[-1] = f'{last_cell:.0f}' if isinstance(last_cell, (int, float)) and np.isfinite(last_cell) and last_cell == int(last_cell) else f'{last_cell:.2f}' if isinstance(last_cell, (int, float)) and np.isfinite(last_cell) else last_cell
        return row
    
    def convert_to_numeric(df, columns):
        """
        Converts specified columns of a DataFrame to numeric.

        Args:
            df (DataFrame): The DataFrame to convert.
            columns (list): The names of the columns to convert.

        Returns:
            DataFrame: The converted DataFrame.
        """
        for column in columns:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors='coerce')
        return df
    
class PesoAtingimento:
    @staticmethod
    def atingimento_com_peso(row, row_names):
        """
        Calculates the weighted achievement for a row in the DataFrame.

        Args:
            row (Series): The row to process.
            row_names (list): The names of the rows to process.

        Returns:
            Series: The processed row.
        """
        meta = row['Meta']
        peso = row['Peso']
        row_name = row.name
        if row_name in row_names:
            return pd.Series([peso if isinstance(val, (int, float)) and val <= meta else 0 if isinstance(val, (int, float)) else None for val in row], index=row.index)
        else:
            return pd.Series([peso if isinstance(val, (int, float)) and val >= meta else (val / meta) * peso if isinstance(val, (int, float)) else None for val in row], index=row.index)

    @staticmethod
    def process(df, row_names):
        """
        Processes the DataFrame and applies the weighted achievement calculation.

        Args:
            df (DataFrame): The DataFrame to process.
            row_names (list): The names of the rows to process.

        Returns:
            DataFrame: The processed DataFrame.
        """
        df['Meta'] = pd.to_numeric(df['Meta'], errors='coerce')
        df['Peso'] = pd.to_numeric(df['Peso'], errors='coerce')

        df.dropna(subset=['Meta'], inplace=True)
        df = df.apply(lambda row: PesoAtingimento.atingimento_com_peso(row, row_names), axis=1)
        df = df.fillna(0)
        totals = df.sum()
        df.loc['Atingimento Total'] = totals
        df = df.drop(['Meta', 'Peso'], axis=1)
        df = df.applymap(lambda x: f'{x:.0f}%' if x == int(x) else f'{x:.2f}%')
        return df


