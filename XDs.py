import streamlit as st
import pandas as pd
from utils import EstilizarPagina, GerarTabelas, filter_by_multiselect, FormatoNumeros, PesoAtingimento
from graficos import Charts
from estilizador import Dataframes
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from functools import reduce
import time

estilizador = EstilizarPagina()
estilizador.set_page_config()

text = "Dados carregando... Duração entre 1 e 5 minutos ⌛"
loading_message = st.empty()
loading_message.progress(0, text=text)

last_month = pd.to_datetime('today') - pd.DateOffset(months=1)

tabela = GerarTabelas()
filenames = ["opav", "produtividade", "inventario", "abs", "two_hrs", "sla", "loss"]
dfs = [tabela.gerar_dados(filename) for filename in filenames]
dados_looker = reduce(lambda left,right: pd.merge(left,right,on=['routing_code', 'month'], how='outer', validate="many_to_many"), dfs)

sheet_names = ['fonte_oficial', 'peso_kpis', 'fonte_metas']
dados_planilha, dados_pesos, dados_metas_planilha = [GerarTabelas.gerar_tabela_sheets(name) for name in sheet_names]

dados_looker = Dataframes.preprocess(dados_looker, 'type_dc', 'Crossdocking')
dados_planilha = Dataframes.preprocess(dados_planilha, 'BASE', 'XD')
dados_metas_planilha = Dataframes.preprocess(dados_metas_planilha, 'BASE', 'XD')
dados_pesos = Dataframes.preprocess(dados_pesos, 'BASE', 'XD')

ABSENTEISMO_PERCENT = 'Absenteísmo (%)'
ABS = 'Absenteísmo'
HE = 'Total de ocorrências de +2HE'
AUTOAVALIACAO = 'Auto avaliação'
AUDITORIA = 'Auditoria'
OPAV = 'OPAV'
ADERENCIA = 'Aderência ao Plano de Capacitação da Qualidade definido para a Base'
INTER = 'Total de ocorrências de -11Hs Interjornadas'
CUSTO = 'Custo / Pacote'
CUSTOXD = 'Custo/ Pacote ($) XDs'
PRODUTIVIDADE = 'Produtividade'
PRODMEDIA = 'Produtividade Média'
LOSS = 'Loss Rate ($)'
LR = 'Loss Rate'
INVENTARIO = 'Inventario (%) XDs'
PROGRAMA5S_PERCENT = 'Programa 5S (%)'
PROGRAMA5S = 'Programa 5S'

columns_planilha = [AUDITORIA, AUTOAVALIACAO,PROGRAMA5S, ADERENCIA, CUSTO]
columns_metas_pesos = [AUDITORIA, AUTOAVALIACAO,PROGRAMA5S_PERCENT, OPAV, PRODUTIVIDADE, LOSS, ABSENTEISMO_PERCENT, ADERENCIA, INVENTARIO, CUSTOXD]

dados_planilha = FormatoNumeros.convert_to_numeric(dados_planilha, columns_planilha)
dados_metas_planilha = FormatoNumeros.convert_to_numeric(dados_metas_planilha, columns_metas_pesos)
dados_pesos = FormatoNumeros.convert_to_numeric(dados_pesos, columns_metas_pesos)

dados_compilados = pd.merge(dados_looker, dados_planilha, on=['month', 'routing_code'], how='inner')

dados_compilados['month'] = dados_compilados['month'].dt.to_timestamp().dt.strftime('%Y-%m')
dados_compilados = dados_compilados.drop(['sla'], axis=1, errors='ignore')

dados_pesos[[ HE, INTER,PRODUTIVIDADE, INVENTARIO, LOSS, CUSTOXD]] = dados_pesos[[ HE, INTER,PRODUTIVIDADE, INVENTARIO, LOSS, CUSTOXD]] * 100
dados_pesos[[PROGRAMA5S_PERCENT]] = dados_pesos[[PROGRAMA5S_PERCENT]] * 10

dados_compilados, dados_metas_planilha = filter_by_multiselect(dados_compilados, dados_metas_planilha, "routing_code", "Routing Code")

dados_compilados.rename(columns={'month': 'Mês', 'opav': OPAV, 'produtividade_media': 'Produtividade Média', 'loss_rate': LR,'Auto avaliacao':AUTOAVALIACAO,'backlog':'Backlog','two_hrs':'Ocorrências de +2HE','abs':ABS,'cnt_interjornada':'Ocorrências de -11Hs Interjornadas', 'percent_inventoried': 'Inventário' }, inplace=True)
dados_metas_planilha.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: 'Ocorrências de +2HE', INTER:'Ocorrências de -11Hs Interjornadas', PRODUTIVIDADE:'Produtividade Média', PROGRAMA5S_PERCENT: PROGRAMA5S, INVENTARIO: 'Inventário', LOSS: LR, CUSTOXD: CUSTO}, inplace=True)
dados_pesos.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: 'Ocorrências de +2HE', INTER:'Ocorrências de -11Hs Interjornadas', PRODUTIVIDADE:'Produtividade Média', PROGRAMA5S_PERCENT: PROGRAMA5S, INVENTARIO: 'Inventário', LOSS: LR, CUSTOXD: CUSTO}, inplace=True)

dados_lex_gauge = dados_compilados[dados_compilados['Mês'] == last_month.strftime('%Y-%m')]
tabela_pivot = dados_compilados.pivot_table(columns='Mês', aggfunc='median')
tabela_pivot = tabela_pivot.reset_index()

metas_pivot = Dataframes.ajustar_pivotar(dados_metas_planilha)
pesos_pivot = Dataframes.ajustar_pivotar(dados_pesos)

def process_and_reset(df, rows=None):
    if rows:
        df.loc[rows] *= 10
    return df.reset_index()

metas_pivot = process_and_reset(metas_pivot, [PROGRAMA5S])
pesos_pivot = process_and_reset(pesos_pivot)

combined_df = pd.merge(tabela_pivot, metas_pivot, left_on='index', right_on='index', how='left')

dados_mergeados_meta = Dataframes.rename_and_move_to_end(combined_df, metas_pivot, 'Meta')
tabela_com_pesos = pd.merge(dados_mergeados_meta, pesos_pivot, left_on='index', right_on='index', how='left')
dados_mergeados_meta = Dataframes.rename_and_move_to_end(tabela_com_pesos, pesos_pivot, 'Peso')
dados_mergeados_meta.set_index(dados_mergeados_meta.columns[0], inplace=True)
dados_mergeados_meta.index.name = None
dados_mergeados_meta = dados_mergeados_meta.fillna('')

dados_mergeados_meta.loc[[OPAV, ABS,AUDITORIA,AUTOAVALIACAO, ADERENCIA]] *= 100
dados_mergeados_meta.loc[[PROGRAMA5S]] *= 10

pivot_table_reset = dados_mergeados_meta.copy()

row_labels_percent = [OPAV, ABS,AUDITORIA,AUTOAVALIACAO, 'Inventário', ADERENCIA, PROGRAMA5S]
row_labels = [PROGRAMA5S,'Ocorrências de +2HE','Ocorrências de -11Hs Interjornadas','Produtividade Média']
row_labels_finance = [CUSTO, LR]

pivot_table_reset = FormatoNumeros.format_rows(pivot_table_reset, row_labels_percent, FormatoNumeros.format_func_percent)
pivot_table_reset = FormatoNumeros.format_rows(pivot_table_reset, row_labels, FormatoNumeros.format_func)
pivot_table_reset = FormatoNumeros.format_rows(pivot_table_reset, row_labels_finance, FormatoNumeros.format_func_finance)

row_names = ['Ocorrências de +2HE','Ocorrências de -11Hs Interjornadas',ABS,CUSTO,LR,OPAV]
tabela_com_pesos_styled = PesoAtingimento.process(dados_mergeados_meta, row_names)

centered_table = Dataframes.generate_html(tabela_com_pesos_styled)
tabela_detalhamento = Dataframes.generate_html(pivot_table_reset)

on = st.toggle('Visualizar detalhamento dos resultados')

if on:
    st.write("  ")
    st.write("  ")
    st.write(centered_table, unsafe_allow_html=True)
    st.write("  ")
    st.divider()
    st.subheader('Detalhamento dos resultados')
    st.write(tabela_detalhamento, unsafe_allow_html=True)
    st.write("  ")
    st.write("  ")
else:
    st.write("  ")
    st.write("  ")
    st.write(centered_table, unsafe_allow_html=True)
    st.write("  ")
    st.write("  ")

dados_compilados['Mês'] = pd.to_datetime(dados_compilados['Mês'])
dados_compilados.set_index('Mês', inplace=True)

estilizador = EstilizarPagina()
estilizador.display_infos()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Pessoas","Qualidade","Entrega", "Financeiro", "Auditoria"])

with tab1:

    col1, col2 = st.columns([1.1, 1])
    column_name = ADERENCIA
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, 'Aderência ao Plano de Capacitação da Qualidade', f"Meta: {meta_value_percent}%", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, 'Aderência ao Plano de Capacitação da Qualidade', meta_value_decimal, 'green', 'red', 0, 1, [0.9, 1], [0, 0.9]))

    col1, col2 = st.columns([1.1, 1])
    column_name = ABS
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, ABS, f"Meta: {meta_value_percent}%", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, ABS, meta_value_decimal, 'green', 'red', 0, 0.1, [meta_value_decimal, 0.1], [0, meta_value_decimal]))

    col1, col2 = st.columns([1.1, 1])
    column_name = 'Ocorrências de +2HE'
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, 'Ocorrências de +2HE', f"Meta: {meta_value_str}", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, 'Ocorrências de +2HE', meta_value_decimal, 'red', 'green', 0, 100, [0, 0], [0, 100]))

    col1, col2 = st.columns([1.1, 1])
    column_name = 'Ocorrências de -11Hs Interjornadas'
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, 'Ocorrências de -11Hs Interjornadas', f"Meta: {meta_value_str}", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, 'Ocorrências de -11Hs Interjornadas', meta_value_decimal, 'red', 'green', 0, 100, [0, 0], [0, 100]))

with tab2:

    col1, col2 = st.columns([1.1, 1])
    column_name = OPAV
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, OPAV, f"Meta: {meta_value_percent}%", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, OPAV, meta_value_decimal, 'red', 'green', 0, 1, [0, meta_value_decimal], [meta_value_decimal, 1]))

    col1, col2 = st.columns([1.1, 1])
    column_name = PROGRAMA5S
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, PROGRAMA5S, f"Meta: {meta_value_percent}%", meta_value_decimal*10, meta_value_decimal*10))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, PROGRAMA5S, meta_value_decimal*10, 'green', 'red', 0, 10, [meta_value_decimal*10, 10], [0, meta_value_decimal*10]))

    col1, col2 = st.columns([1.1, 1])
    column_name = 'Inventário'
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, 'Inventário', f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, 'Inventário', meta_value_decimal, 'green', 'red', 0, 100, [meta_value_decimal, 100], [0, meta_value_decimal]))

loading_message.progress(80, text=text)

with tab3:

    col1, col2 = st.columns([1.1, 1])
    column_name = 'Produtividade Média'
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, 'Produtividade Média', f"Meta: {meta_value_str}", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, 'Produtividade Média', meta_value_decimal, 'green', 'red', 0, 1500, [meta_value_decimal, 1500], [0, meta_value_decimal]))

with tab4:

    col1, col2 = st.columns([1.1, 1])
    column_name = LR
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, LR, f"Meta: R${meta_value_str}", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, LR, meta_value_decimal, 'red', 'green', 0, 1, [0, meta_value_decimal], [meta_value_decimal, 1]))

    col1, col2 = st.columns([1.1, 1])
    column_name = CUSTO
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, CUSTO, f"Meta: R${meta_value_str}", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, CUSTO, meta_value_decimal, 'red', 'green', 0, 10, [0, meta_value_decimal], [meta_value_decimal, 10]))

with tab5:

    col1, col2 = st.columns([1.1, 1])
    column_name = AUDITORIA
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, AUDITORIA, f"Meta: {meta_value_str}", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, AUDITORIA, meta_value_decimal, 'green', 'red', 0, 1.2,[meta_value_decimal, 1.2], [0, meta_value_decimal]))

    col1, col2 = st.columns([1.1, 1])
    column_name = AUTOAVALIACAO
    dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
    meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
    col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, AUTOAVALIACAO, f"Meta: {meta_value_str}", meta_value_decimal, meta_value_decimal))
    col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, AUTOAVALIACAO, meta_value_decimal, 'green', 'red', 0, 1.2, [meta_value_decimal, 1.2], [0, meta_value_decimal]))

loading_message.progress(100, text=text)
time.sleep(1)
loading_message.empty()

 
