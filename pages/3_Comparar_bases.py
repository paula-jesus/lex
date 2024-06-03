import streamlit as st
from utils import EstilizarPagina
from visao_comparativa import comparativo
import time
from consts import *

estilizador = EstilizarPagina()
estilizador.set_page_config()

text = "Dados carregando... Duração entre 1 e 5 minutos ⌛"
loading_message = st.empty()
loading_message.progress(0, text=text)

st.info("Esse link será desativado em breve. Acesse o novo [link oficial](https://lex.platform.loggi.com/) (você precisará logar na sua conta Loggi para acessar).")

loading_message.progress(30, text=text)

tab1, tab2 = st.tabs(["Agências","XDs"])

with tab1:
    
    comparativo('Ag')

with tab2:

    comparativo('XD')

loading_message.progress(100, text=text)
time.sleep(1)
loading_message.empty()
