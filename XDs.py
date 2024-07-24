import streamlit as st
import time
from trat_graficos import create_charts
from estilizador import Dataframes, Page_config
from consts import *
import streamlit as st
from create_dataframes_h2 import create_tables

estilizador = Page_config()
estilizador.set_page_config()

text = "Dados carregando... Duração entre 1 e 5 minutos ⌛"
loading_message = st.empty()
loading_message.progress(0, text=text)

resultados, resultados_geral, _, bsc_geral_styled, _, metas, _ = create_tables('XD')

loading_message.progress(50, text=text)

Dataframes.gerar_tabela_final(bsc_geral_styled, resultados_geral)

loading_message.progress(70, text=text)

create_charts(metas, resultados, 'XD')

loading_message.progress(100, text=text)
time.sleep(1)
loading_message.empty()