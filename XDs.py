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

st.info("Esse link será desativado no dia 29/05. Acesse o novo [link oficial](https://lex.platform.loggi.com/) (você precisará logar na sua conta Loggi para acessar).")

tabela_com_pesos_styled, pivot_table_reset, dados_compilados, dados_metas_planilha, dados_lex_gauge, dados_metas_pesos, comparativo_pesos, detalhamento_comparativo, dados_pesos, pesos_pivot = process_data('Crossdocking', 'XD', 'xxds')
loading_message.progress(30, text=text)

Dataframes.gerar_tabela_final(tabela_com_pesos_styled, pivot_table_reset)

estilizador = EstilizarPagina()
estilizador.display_infos()
loading_message.progress(70, text=text)

trat_graficos('XD')

loading_message.progress(100, text=text)
time.sleep(1)
loading_message.empty()

 
