
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

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
            "page_title": "BSC LEX",
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

class GerarTabela:
    """
    This class is responsible for generating tables by reading SQL files.

    Args:
        _self (object): Instance of the class. Self with undercore is used to cache the data and avoid conflicts with streamlit. More informations about it here: https://discuss.streamlit.io/t/from-st-cache-to-st-cache-data-in-a-class/37667
    """
    def __init__(_self):
        _self.leitor = DataReader()

    @st.cache_data(show_spinner=False, ttl=840000)
    def gerar_dados_lex(_self):
        """
        This method reads the 'dados_lex.sql' file and returns its content.

        Args:
            _self (object): Instance of the class. 

        Returns:
            DataFrame: A pandas DataFrame containing the data read from 'dados_cs.sql'.
        """
        return _self.leitor.read_sql("SQL", "dados_lex.sql")
    
    @st.cache_data(show_spinner=False, ttl=840000)
    def gerar_dados_opav(_self):
        """
        This method reads the 'dados_opav.sql' file and returns its content.

        Args:
            _self (object): Instance of the class. 

        Returns:
            DataFrame: A pandas DataFrame containing the data read from 'opav.sql'.
        """
        return _self.leitor.read_sql("SQL", "opav.sql")
    
    @st.cache_data(show_spinner=False, ttl=840000)
    def gerar_dados_produtividade(_self):
        """
        This method reads the 'dados_produtividade.sql' file and returns its content.

        Args:
            _self (object): Instance of the class. 

        Returns:
            DataFrame: A pandas DataFrame containing the data read from 'produtividade.sql'.
        """
        return _self.leitor.read_sql("SQL", "produtividade.sql")
    
    @st.cache_data(show_spinner=False, ttl=840000)
    def gerar_dados_inventario(_self):
        """
        This method reads the 'inventario.sql' file and returns its content.

        Args:
            _self (object): Instance of the class. 

        Returns:
            DataFrame: A pandas DataFrame containing the data read from 'inventario.sql'.
        """
        return _self.leitor.read_sql("SQL", "inventario.sql")
    
    @st.cache_data(show_spinner=False, ttl=840000)
    def gerar_dados_sla(_self):
        """
        This method reads the 'sla.sql' file and returns its content.

        Args:
            _self (object): Instance of the class. 

        Returns:
            DataFrame: A pandas DataFrame containing the data read from 'sla.sql'.
        """
        return _self.leitor.read_sql("SQL", "sla.sql")
    
    @st.cache_data(show_spinner=False, ttl=840000)
    def gerar_dados_abs(_self):
        """
        This method reads the 'abs.sql' file and returns its content.

        Args:
            _self (object): Instance of the class. 

        Returns:
            DataFrame: A pandas DataFrame containing the data read from 'abs.sql'.
        """
        return _self.leitor.read_sql("SQL", "abs.sql")
    
    @st.cache_data(show_spinner=False, ttl=840000)
    def gerar_dados_two_hrs(_self):
        """
        This method reads the 'two_hrs.sql' file and returns its content.

        Args:
            _self (object): Instance of the class. 

        Returns:
            DataFrame: A pandas DataFrame containing the data read from 'two_hrs.sql'.
        """
        return _self.leitor.read_sql("SQL", "two_hrs.sql")
    
    


st.cache_data(show_spinner=False, ttl=840000)
def gerar_tabela_sheets(key, worksheet):
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
    sh = gc.open_by_key(key)
    worksheet_list = sh.worksheets()

    ws = sh.worksheet(worksheet)
    data = ws.get_values(value_render_option="UNFORMATTED_VALUE", date_time_render_option="FORMATTED_STRING")

    df = pd.DataFrame(data[1:], columns=data[0])

    return df


def create_area_plot(df, y_column, title, text, y0, y1):
    # Create the area plot
    plot = px.area(df, x="Mês", y=y_column, title=title, height=330, width=500, color_discrete_sequence=['#00baff'])

    goal_line = go.layout.Shape(
        type="line",
        x0=df["Mês"].min(),
        x1=df["Mês"].max(),
        y0=y0,
        y1=y1,
        line=dict(
            color="#148bb8",
            width=2,
            dash="dashdot",
        ),
    )

    #Add an annotation
    plot.add_annotation(
        x=df["Mês"].max(),
        y=y0,
        text=text,
        showarrow=False,
        font=dict(
            size=16,
            color="#148bb8"
        ),
        bgcolor="White",
        bordercolor="#148bb8",
        borderwidth=2,
        borderpad=4,
    )

    plot.update_layout(shapes=[goal_line], showlegend=False, yaxis_title=None)

    return plot

def filter_by_multiselect(df1, df2, column, label):
    selected_values = st.sidebar.multiselect(label, df1[column].unique(), key=label)
    if selected_values:
        df1 = df1[df1[column].isin(selected_values)]
        df2 = df2[df2[column].isin(selected_values)]
    return df1, df2

def create_gauge_chart(df, column, title, green1, green2, red1, red2, x=1, y=0):
    value = df[column].median()
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': 0.03, 'increasing': {'color': "red"}, 'decreasing': {'color': "black"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [y, x]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [green1, green2], 'color': '#c9f1ac'},  # Green
                    {'range': [red1, red2], 'color': '#fab8a3'},  # Red
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ),
        layout={'width': 500, 'height': 320}  # Adjust the width and height as needed
    )
    return fig
