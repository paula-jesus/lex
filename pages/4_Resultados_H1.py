import streamlit as st
from estilizador import Page_config
from resultados_h1 import tabelas_resultados_h1
import time
from consts import *

estilizador = Page_config()
estilizador.set_page_config()

text = "Dados carregando... Duração entre 1 e 5 minutos ⌛"
loading_message = st.empty()
loading_message.progress(0, text=text)

st.header("Resultado H1")

loading_message.progress(30, text=text)

tab1, tab2 = st.tabs(["Agências","XDs"])

with tab1:
    
    tabelas_resultados_h1('Ag', 'ag_h1')

with tab2:

    tabelas_resultados_h1('XD', 'xd_h1')

loading_message.progress(100, text=text)
time.sleep(1)
loading_message.empty()