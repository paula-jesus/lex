import streamlit as st
from utils import EstilizarPagina
from trat_dataframes import process_data, comparativo
import time
from trat_graficos import trat_graficos
from estilizador import Dataframes
from consts import *
import plotly.express as px
import pandas as pd

estilizador = EstilizarPagina()
estilizador.set_page_config()

text = "Dados carregando... Duração entre 1 e 5 minutos ⌛"
loading_message = st.empty()
loading_message.progress(0, text=text)

loading_message.progress(30, text=text)

tab1, tab2 = st.tabs(["Agências","XDs"])

with tab1:
    
    comparativo('Ag')

with tab2:

    comparativo('XD')

loading_message.progress(100, text=text)
time.sleep(1)
loading_message.empty()