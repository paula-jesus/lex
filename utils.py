import pandas as pd
import streamlit as st
import numpy as np

from leitor import DataReader

import pandas as pd
import gspread
import warnings

warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)  

class GerarTabelas:
    """
    This class is responsible for generating tables by reading SQL files.

    Args:
        _self (object): Instance of the class. Self with undercore is used to cache the data and avoid conflicts with streamlit. More inions about it here: https://discuss.streamlit.io/t/from-st-cache-to-st-cache-data-in-a-class/37667
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
    
# class Ajustes_tabelas:
#     def rename_columns_before_merge(df, suffix, exclude_cols=[]):
#         df_copy = df.copy()
#         df_copy.columns = [f"{col} {suffix}" if col not in exclude_cols else col for col in df_copy.columns]
#         return df_copy

#     def convert_month(dfs):
#         for df in dfs:
#             df['month'] = pd.to_datetime(df['month']).dt.to_period('M')
#         return dfs

#     def change_na(dfs):
#         for df in dfs:
#             df.replace("N/A", "", inplace=True)
#         return dfs

#     def config_columns_numeric(dfs):
#         for df in dfs:
#             colunas = ['% Participação em Treinamentos [Loggers]', '% Participação em Treinamentos [Líderes]', '% Aprovação em Treinamentos [Loggers]', '% Aprovação em Treinamentos [Líderes]', '% Cumprimento das Rotinas da Qualidade', '% Conformidade [Inspeções da Qualidade]', '% Atingimento da Auditoria Oficial', '% Programa 5S  [XD]', 'IQR Moto', 'IQR Carro']
#             for coluna in colunas:
#                 if coluna in df.columns:
#                     df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

#     def gerar_tabelas(self):
#         tabela = GerarTabelas()
#         filenames = ["opav", "abs", "sla", "iqr"]
#         dfs = [tabela.gerar_dados(filename) for filename in filenames]
#         dados_looker = reduce(lambda left,right: pd.merge(left,right,on=['routing_code', 'month'], how='outer', validate="many_to_many"), dfs)

#         sheet_names = ['fonte_oficial_h2', 'peso_kpis_h2_2024', 'fonte_metas_h2_2024']
#         dados_planilha, pesos, metas = [GerarTabelas.gerar_tabela_sheets(name) for name in sheet_names]

#         return dados_looker, dados_planilha, pesos, metas

#     def ajustes_iniciais(type):
#         ajustes_tabelas = Ajustes_tabelas()
#         dados_looker, dados_planilha, pesos, metas = ajustes_tabelas.gerar_tabelas()
#         dados_looker['routing_code'] = dados_looker['routing_code'].replace('CJ2', 'XDCJ2')
#         dados_looker = dados_looker.rename(columns={'sla': 'SLA', 'abs': '% Absenteísmo', 'opav': 'OPAV', 'iqr_moto': 'IQR Moto', 'iqr_carro': 'IQR Carro'})
#         Ajustes_tabelas.convert_month([dados_looker, dados_planilha, pesos, metas])
#         Ajustes_tabelas.change_na([dados_looker, dados_planilha, pesos, metas])
#         Ajustes_tabelas.config_columns_numeric([dados_looker, dados_planilha, pesos, metas])
#         dados_planilha = dados_planilha.drop('#', axis=1)

#         dados_planilha = dados_planilha[dados_planilha['BASE'] == type]
#         metas = metas[metas['BASE'] == type]
#         pesos = pesos[pesos['BASE'] == type]

#         if type == 'XD':
#             dados_looker = dados_looker[['routing_code', 'month', 'SLA', '% Absenteísmo', 'OPAV']]
#         if type == 'Ag':
#             dados_planilha = dados_planilha[['routing_code', 'month', '% Participação em Treinamentos [Loggers]', '% Participação em Treinamentos [Líderes]', '% Aprovação em Treinamentos [Loggers]', '% Aprovação em Treinamentos [Líderes]', '% Cumprimento das Rotinas da Qualidade', '% Atingimento da Auditoria Oficial']]

#         resultados = pd.merge(dados_planilha, dados_looker, on=['routing_code', 'month'], how='left')
#         resultados.rename(columns={'month': 'Mês', 'routing_code': 'Routing Code'}, inplace=True)
#         metas.rename(columns={'month': 'Mês', 'routing_code': 'Routing Code'}, inplace=True)
#         pesos.rename(columns={'month': 'Mês', 'routing_code': 'Routing Code'}, inplace=True)
#         resultados.columns = resultados.columns.str.replace('% ', '')
#         metas.columns = metas.columns.str.replace('% ', '')
#         pesos.columns = pesos.columns.str.replace('% ', '')

#         return resultados, pesos, metas
    
# class CalcularPesos:    

#     def calculate_columns(resultados_com_peso_meta, columns):
#         for column in columns:
#             resultados_com_peso_meta[f'{column} peso'] = resultados_com_peso_meta[f'{column} peso'].astype(float) * 100
#             resultados_com_peso_meta[f'{column} resultado'] = resultados_com_peso_meta[f'{column} resultado'].astype(float)
#             resultados_com_peso_meta[f'{column} meta'] = resultados_com_peso_meta[f'{column} meta'].astype(float)
#             resultados_com_peso_meta[f'{column}'] = np.minimum(resultados_com_peso_meta[f'{column} peso'], (resultados_com_peso_meta[f'{column} resultado'] / resultados_com_peso_meta[f'{column} meta']) * resultados_com_peso_meta[f'{column} peso'])

#     def calculate_columns_baixo_melhor(resultados_com_peso_meta, columns):
#         for column in columns:
#             resultados_com_peso_meta[f'{column} peso'] = resultados_com_peso_meta[f'{column} peso'].astype(float) * 100
#             resultados_com_peso_meta[f'{column} resultado'] = resultados_com_peso_meta[f'{column} resultado'].astype(float)
#             resultados_com_peso_meta[f'{column} meta'] = resultados_com_peso_meta[f'{column} meta'].astype(float)
#             condition = (resultados_com_peso_meta[f'{column} resultado'] > resultados_com_peso_meta[f'{column} meta']) & (resultados_com_peso_meta[f'{column} resultado'].notna()) & (resultados_com_peso_meta[f'{column} meta'].notna())
#             resultados_com_peso_meta.loc[condition, f'{column}'] = 0
#             resultados_com_peso_meta.loc[~condition & resultados_com_peso_meta[f'{column} resultado'].notna() & resultados_com_peso_meta[f'{column} meta'].notna(), f'{column}'] = resultados_com_peso_meta[f'{column} peso']



class FormatoNumeros:
    def format_rows(df, row_labels, format_func, key=None):
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
        row = row.apply(lambda x: f'{x:.0f}%' if isinstance(x, (int, float)) and np.isfinite(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (int, float)) and np.isfinite(x) else x)
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
    
    def format_func_finance(row, key=None):
        """
        Formats a row of a DataFrame as currency values.

        Args:
            row (Series): The row to format.

        Returns:
            Series: The formatted row.
        """
        row = row.apply(lambda x: f'R$ {x:.0f}' if isinstance(x, (int, float)) and np.isfinite(x) and x == int(x) else f'R$ {x:.2f}' if isinstance(x, (int, float)) and np.isfinite(x) else x)
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
    
    
def color_achievement(row, type):
        try:
            peso = row[type].replace('%', '')
        except (AttributeError, ValueError):
                peso = str(row[type]).replace('%', '')
        peso = peso.replace('R$ ', '')
        peso = float(peso)
        colors = []
        for i, val in enumerate(row):
            if i == len(row) - 1:
                colors.append('')  # No color for the last column
                continue
            try:
                val = str(val).replace('%', '')
                val = str(val).replace('R$ ', '')
                val = str(val).replace(' ', '')
                val = float(val)
                if type == 'Peso': 
                    if val < 0.25 * peso:
                        colors.append('background-color: #f4c6c9')  # light red
                    elif val < 0.5 * peso:
                        colors.append('background-color: #fae1b9')  # light orange
                    elif val < 0.85 * peso:
                        colors.append('background-color: #f6edbd')  # light yellow
                    elif val < peso:
                        colors.append('background-color: #d9e8c3')  # light green
                    elif val >= peso:
                        colors.append('background-color: #8be0b8')
                    else:
                        colors.append('background-color: #7f8773')
                else:
                    colors.append('background-color: #FFFFFF')  # default color if val can't be converted to float
            except ValueError:
                colors.append('background-color: #FFFFFF')  # default color if val can't be converted to float
        return colors