import streamlit as st
from utils import EstilizarPagina
from trat_dataframes import process_data
import time
from trat_graficos import trat_graficos
from estilizador import Dataframes

estilizador = EstilizarPagina()
estilizador.set_page_config()

text = "Dados carregando... Duração entre 1 e 5 minutos ⌛"
loading_message = st.empty()
loading_message.progress(0, text=text)

centered_table, tabela_detalhamento, dados_compilados_xd, dados_lex_gauge, dados_metas_planilha_xd = process_data('Crossdocking', 'XD')
loading_message.progress(30, text=text)

Dataframes.gerar_tabela_final(centered_table, tabela_detalhamento)

estilizador = EstilizarPagina()
estilizador.display_infos()
loading_message.progress(70, text=text)

trat_graficos('XD')

loading_message.progress(100, text=text)
time.sleep(1)
loading_message.empty()

 
