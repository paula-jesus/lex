import streamlit as st
import pandas as pd
from utils import EstilizarPagina, GerarTabela, gerar_tabela_sheets, create_area_plot, filter_by_multiselect
from estilizador import DataframeStyler, PageStyler
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

tabela = GerarTabela()
dados_opav = tabela.gerar_dados_opav()
dados_produtividade = tabela.gerar_dados_produtividade()
dados_inventario = tabela.gerar_dados_inventario()
dados_abs = tabela.gerar_dados_abs()
dados_two_hrs = tabela.gerar_dados_two_hrs()
dados_sla = tabela.gerar_dados_sla()

loading_message.progress(30, text=text)

# List of all dataframes
dfs = [dados_opav, dados_produtividade, dados_inventario, dados_abs, dados_two_hrs, dados_sla]

dados_looker = reduce(lambda left,right: pd.merge(left,right,on=['routing_code', 'month'], how='outer'), dfs)

dados_planilha = gerar_tabela_sheets('1wQs6k5eGKASNxSMYcfHwP5HK7PSEDo0t_uzLYke_u3s','fonte_oficial')
dados_pesos = gerar_tabela_sheets('1wQs6k5eGKASNxSMYcfHwP5HK7PSEDo0t_uzLYke_u3s','peso_kpis')

dados_metas_planilha = gerar_tabela_sheets('1wQs6k5eGKASNxSMYcfHwP5HK7PSEDo0t_uzLYke_u3s','fonte_metas')

mask = dados_looker['type_dc'] == 'Crossdocking'
dados_looker = dados_looker[mask]

mask = dados_metas_planilha['BASE'] == 'XD'
dados_metas_planilha = dados_metas_planilha[mask]

mask = dados_pesos['BASE'] == 'XD'
dados_pesos = dados_pesos[mask]

dados_planilha = dados_planilha.drop('#', axis=1)

dados_metas_planilha = dados_metas_planilha.drop('#', axis=1)

dados_pesos = dados_pesos.drop('#', axis=1)

dados_looker['month'] = pd.to_datetime(dados_looker['month'])
dados_looker['month'] = dados_looker['month'].dt.strftime('%Y-%m')
mask = dados_looker['month'] > '2023-12'
dados_looker = dados_looker[mask]

for column in ['Auditoria', 'Auto avaliação','Programa 5S', 'Aderência ao Plano de Capacitação da Qualidade definido para a Base']:
    dados_planilha[column] = pd.to_numeric(dados_planilha[column], errors='coerce')

for column in ['Auditoria', 'Auto avaliação','Programa 5S (%)', 'OPAV', 'Produtividade', 'Loss Rate ($)', 'Absenteísmo (%)', 'Aderência ao Plano de Capacitação da Qualidade definido para a Base', 'Inventario (%) XDs', 'Custo/ Pacote ($) XDs']:
    dados_metas_planilha[column] = pd.to_numeric(dados_metas_planilha[column], errors='coerce')

for column in ['Auditoria', 'Auto avaliação','Programa 5S (%)', 'OPAV', 'Produtividade', 'Loss Rate ($)', 'Absenteísmo (%)', 'Aderência ao Plano de Capacitação da Qualidade definido para a Base', 'Inventario (%) XDs', 'Custo/ Pacote ($) XDs']:
    dados_pesos[column] = pd.to_numeric(dados_pesos[column], errors='coerce')

dados_looker['month'] = pd.to_datetime(dados_looker['month']).dt.to_period('M')
dados_planilha['month'] = pd.to_datetime(dados_planilha['month']).dt.to_period('M')

dados_metas_planilha['month'] = pd.to_datetime(dados_metas_planilha['month']).dt.to_period('M')
dados_pesos['month'] = pd.to_datetime(dados_pesos['month']).dt.to_period('M')
########lembrar de calcular o resultado com variacao por mes########

dados_planilha['routing_code'] = dados_planilha['routing_code'].replace('XDCJ2', 'CJ2')
dados_metas_planilha['routing_code'] = dados_metas_planilha['routing_code'].replace('XDCJ2', 'CJ2')
dados_pesos['routing_code'] = dados_pesos['routing_code'].replace('XDCJ2', 'CJ2')

dados_planilha = dados_planilha.replace('N/A', '')

dados_metas_planilha = dados_metas_planilha.replace('N/A', '')

dados_pesos = dados_pesos.replace('N/A', '')

dados_compilados = pd.merge(dados_looker, dados_planilha, on=['month', 'routing_code'], how='left')

dados_compilados['month'] = dados_compilados['month'].dt.to_timestamp().dt.strftime('%Y-%m')

dados_pesos[[ 'Total de ocorrências de +2HE', 'Total de ocorrências de -11Hs Interjornadas','Produtividade', 'Inventario (%) XDs']] = dados_pesos[[ 'Total de ocorrências de +2HE', 'Total de ocorrências de -11Hs Interjornadas','Produtividade', 'Inventario (%) XDs']] * 100

dados_pesos[['Programa 5S (%)']] = dados_pesos[['Programa 5S (%)']] * 10

#Filtros

dados_compilados, dados_metas_planilha = filter_by_multiselect(dados_compilados, dados_metas_planilha, "month", "Mês")

dados_compilados, dados_metas_planilha = filter_by_multiselect(dados_compilados, dados_metas_planilha, "routing_code", "Routing Code")

dados_compilados = dados_compilados.drop(['sla'], axis=1, errors='ignore')

dados_compilados.rename(columns={'month': 'Mês', 'opav': 'OPAV', 'produtividade_media': 'Produtividade Média', 'loss_rate': 'Loss Rate','Auto avaliacao':'Auto avaliação','backlog':'Backlog','two_hrs':'Ocorrências de +2HE','abs':'Absenteísmo','cnt_interjornada':'Ocorrências de -11Hs Interjornadas', 'percent_inventoried': 'Inventário' }, inplace=True)

dados_lex_gauge = dados_compilados[dados_compilados['Mês'] == last_month.strftime('%Y-%m')]

dados_tabela_pivtada = dados_compilados.copy()

dados_tabela_pivtada.rename(columns={'Mês': 'KPIs'}, inplace=True)

pivot_table = dados_tabela_pivtada.pivot_table(columns='KPIs', aggfunc='median')
    
pivot_table = pivot_table.reset_index()

last_month = pd.to_datetime('now').to_period('M') - 1
dados_metas_planilha = dados_metas_planilha[dados_metas_planilha['month'] == last_month]
dados_pesos = dados_pesos[dados_pesos['month'] == last_month]

dados_metas_planilha.rename(columns={'Absenteísmo (%)': 'Absenteísmo','Total de ocorrências de +2HE': 'Ocorrências de +2HE', 'Total de ocorrências de -11Hs Interjornadas':'Ocorrências de -11Hs Interjornadas', 'Produtividade':'Produtividade Média', 'Programa 5S (%)': 'Programa 5S', 'Inventario (%) XDs': 'Inventário'}, inplace=True)
dados_pesos.rename(columns={'Absenteísmo (%)': 'Absenteísmo','Total de ocorrências de +2HE': 'Ocorrências de +2HE', 'Total de ocorrências de -11Hs Interjornadas':'Ocorrências de -11Hs Interjornadas', 'Produtividade':'Produtividade Média', 'Programa 5S (%)': 'Programa 5S', 'Inventario (%) XDs': 'Inventário'}, inplace=True)

metas_pivot = dados_metas_planilha.pivot_table(columns='month', aggfunc='median')

pesos_pivot = dados_pesos.pivot_table(columns='month', aggfunc='median')

metas_pivot.loc[['Programa 5S']] *= 10

metas_pivot = metas_pivot.reset_index()

pesos_pivot = pesos_pivot.reset_index()

combined_df = pd.merge(pivot_table, metas_pivot, left_on='index', right_on='index', how='left')

last_month_column = metas_pivot.columns[-1]

combined_df = combined_df.rename(columns={last_month_column: 'Meta'})

columns = combined_df.columns.tolist()
columns.remove('Meta')
columns.append('Meta')
dados_mergeados_meta = combined_df[columns]

tabela_com_pesos = pd.merge(dados_mergeados_meta, pesos_pivot, left_on='index', right_on='index', how='left')

last_month_column = pesos_pivot.columns[-1]

tabela_com_pesos = tabela_com_pesos.rename(columns={last_month_column: 'Peso'})

columns = tabela_com_pesos.columns.tolist()
columns.remove('Peso')
columns.append('Peso')
dados_mergeados_meta = tabela_com_pesos[columns]

dados_mergeados_meta.set_index(dados_mergeados_meta.columns[0], inplace=True)

dados_mergeados_meta.index.name = None

dados_mergeados_meta = dados_mergeados_meta.fillna('')

dados_mergeados_meta.loc[['OPAV', 'Absenteísmo','Auditoria','Auto avaliação', 'Aderência ao Plano de Capacitação da Qualidade definido para a Base']] *= 100

dados_mergeados_meta.loc[['Programa 5S']] *= 10

pivot_table_reset = dados_mergeados_meta.copy()

# def format_row_with_percent(row):
#     return row.apply(lambda x: f'{x:.0f}%' if isinstance(x, (int, float)) and np.isfinite(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (int, float)) else x)

def format_row_with_percent(row):
    row.iloc[:-1] = row.iloc[:-1].apply(lambda x: f'{x:.0f}%' if isinstance(x, (int, float)) and np.isfinite(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (int, float)) and np.isfinite(x) else x)
    last_cell = row.iloc[-1]
    row.iloc[-1] = f'{last_cell:.0f}' if isinstance(last_cell, (int, float)) and np.isfinite(last_cell) and last_cell == int(last_cell) else f'{last_cell:.2f}' if isinstance(last_cell, (int, float)) and np.isfinite(last_cell) else last_cell
    return row

row_labels = ['OPAV', 'Absenteísmo','Auditoria','Auto avaliação', 'Inventário', 'Aderência ao Plano de Capacitação da Qualidade definido para a Base', 'Programa 5S']  
pivot_table_reset.loc[row_labels] = pivot_table_reset.loc[row_labels].apply(format_row_with_percent, axis=1)

def format_row(row):
    return row.apply(lambda x: f'{x:.0f}' if isinstance(x, (int, float)) and np.isfinite(x) and x == int(x) else f'{x:.2f}' if isinstance(x, (int, float)) and np.isfinite(x) else x)

row_labels = ['Programa 5S','Ocorrências de +2HE','Ocorrências de -11Hs Interjornadas','Produtividade Média']  
pivot_table_reset.loc[row_labels] = pivot_table_reset.loc[row_labels].apply(format_row, axis=1)

rendered_table = pivot_table_reset.to_html()
tabela_detalhamento = f"""
<div style="display: flex; justify-content: center;">
<div style="max-height: 500px; overflow-y: auto;">
        {rendered_table}
"""

def atingimento_com_peso(row):
    meta = row['Meta']
    peso = row['Peso']
    row_name = row.name
    if row_name in ('Ocorrências de +2HE','Ocorrências de -11Hs Interjornadas','Absenteísmo','Custo/ Pacote','Loss Rate','OPAV'):
        return pd.Series([peso if isinstance(val, (int, float)) and val <= meta else 0 if isinstance(val, (int, float)) else None for val in row], index=row.index)
    else:
        return pd.Series([peso if isinstance(val, (int, float)) and val >= meta else (val / meta) * peso if isinstance(val, (int, float)) else None for val in row], index=row.index)
    
dados_mergeados_meta['Meta'] = pd.to_numeric(dados_mergeados_meta['Meta'], errors='coerce')
dados_mergeados_meta['Peso'] = pd.to_numeric(dados_mergeados_meta['Peso'], errors='coerce')

dados_mergeados_meta.dropna(subset=['Meta'], inplace=True)

tabela_com_pesos_styled = dados_mergeados_meta.apply(atingimento_com_peso, axis=1)
    
tabela_com_pesos_styled = tabela_com_pesos_styled.fillna(0)

totals = tabela_com_pesos_styled.sum()

tabela_com_pesos_styled.loc['Atingimento Total'] = totals

tabela_com_pesos_styled = tabela_com_pesos_styled.drop(['Meta', 'Peso'], axis=1)

tabela_com_pesos_styled = tabela_com_pesos_styled.applymap(lambda x: f'{x:.0f}%' if x == int(x) else f'{x:.2f}%')

rendered_table = tabela_com_pesos_styled.to_html()
centered_table = f"""
<div style="display: flex; justify-content: center;">
<div style="max-height: 500px; overflow-y: auto;">
        {rendered_table}
"""

on = st.toggle('Visualizar detalhamento dos resultados (sem considerar peso)')

if on:

    st.write("  ")
    st.write("  ")
    st.write(centered_table, unsafe_allow_html=True)
    st.write("  ")
    st.write("  ")

    st.write("  ")
    st.write("  ")
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

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Pessoas","Qualidade","Entrega", "Financeiro", "Auditoria"])

with tab1:

    col1, col2 = st.columns([1.1, 1])

    dados_compilados['Aderência ao Plano de Capacitação da Qualidade definido para a Base'] = pd.to_numeric(dados_compilados['Aderência ao Plano de Capacitação da Qualidade definido para a Base'], errors='coerce')
    dados_lex_gauge['Aderência ao Plano de Capacitação da Qualidade definido para a Base'] = pd.to_numeric(dados_lex_gauge['Aderência ao Plano de Capacitação da Qualidade definido para a Base'], errors='coerce')
    
    value = dados_compilados['Aderência ao Plano de Capacitação da Qualidade definido para a Base'].median()
    
    dados_lex_resampled = dados_compilados.resample('M')['Aderência ao Plano de Capacitação da Qualidade definido para a Base'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    dados_metas_aderencia = dados_metas_planilha[['Aderência ao Plano de Capacitação da Qualidade definido para a Base']].rename(columns={'Aderência ao Plano de Capacitação da Qualidade definido para a Base': 'meta'})

    meta_value_decimal = dados_metas_aderencia['meta'].median()
    
    meta_value_percent = str(dados_metas_aderencia['meta'].median() * 100)

    meta_value_percent = meta_value_percent.rstrip('0').rstrip('.') if '.' in meta_value_percent else meta_value_percent

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Aderência ao Plano de Capacitação da Qualidade definido para a Base", 'Aderência ao Plano de Capacitação da Qualidade', f"Meta: {meta_value_percent}%", meta_value_decimal, meta_value_decimal))

    value = dados_lex_gauge['Aderência ao Plano de Capacitação da Qualidade definido para a Base'].median()

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Aderência ao Plano de Capacitação da Qualidade", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': 0.9, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 1]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, 0.9], 'color': '#c9f1ac'},  
                    {'range': [0.9, 1], 'color': '#fab8a3'},  
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ),
        layout={
            'annotations': [
                {
                    'x': 0.5,
                    'y': -0.25,
                    'showarrow': False,
                    'text': "Valor referente ao último mês completo",
                    'xref': "paper",
                    'yref': "paper"
                }
            ],
            'width': 500, 
            'height': 320
        }
    )

    col2.plotly_chart(fig)

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['Absenteísmo'].median()
    
    dados_lex_resampled = dados_compilados.resample('M')['Absenteísmo'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    dados_metas_abs = dados_metas_planilha[['Absenteísmo']].rename(columns={'Absenteísmo': 'meta'})

    meta_value_decimal = dados_metas_abs['meta'].median()

    meta_value_percent = str(dados_metas_abs['meta'].median() * 100)

    meta_value_percent = meta_value_percent.rstrip('0').rstrip('.') if '.' in meta_value_percent else meta_value_percent

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Absenteísmo", 'Absenteísmo', f"Meta: {meta_value_percent}%", meta_value_decimal, meta_value_decimal))

    value = dados_lex_gauge['Absenteísmo'].median()

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Absenteísmo", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': meta_value_decimal, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 0.1]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, meta_value_decimal], 'color': '#c9f1ac'},  
                    {'range': [meta_value_decimal, 0.1], 'color': '#fab8a3'},  
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ),
        layout={
            'annotations': [
                {
                    'x': 0.5,
                    'y': -0.25,
                    'showarrow': False,
                    'text': "Valor referente ao último mês completo",
                    'xref': "paper",
                    'yref': "paper"
                }
            ],
            'width': 500, 
            'height': 320
        }
    )

    col2.plotly_chart(fig)

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['Ocorrências de +2HE'].median()  

    dados_lex_resampled = dados_compilados.resample('M')['Ocorrências de +2HE'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    dados_metas_2he = dados_metas_planilha[['Ocorrências de +2HE']].rename(columns={'Ocorrências de +2HE': 'meta'})

    meta_value_decimal = dados_metas_2he['meta'].median()

    meta_value_percent = str(dados_metas_2he['meta'].median())

    meta_value_percent = meta_value_percent.rstrip('0').rstrip('.') if '.' in meta_value_percent else meta_value_percent

    chart = create_area_plot(dados_lex_resampled, "Ocorrências de +2HE", 'Ocorrências de +2HE', f"Meta: {meta_value_percent}", meta_value_decimal, meta_value_decimal)

    col1.plotly_chart(chart)

    value = dados_compilados['Ocorrências de +2HE'].median()  # or any other aggregation
    
    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Ocorrências de +2HE", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': 0, 'increasing': {'color': "red"}, 'decreasing': {'color': "black"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, 100], 'color': '#fab8a3'},  # Red
                    # {'range': [0.1, 1], 'color': '#c9f1ac'},  # Green
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ),
        layout={
            'annotations': [
                {
                    'x': 0.5,
                    'y': -0.25,
                    'showarrow': False,
                    'text': "Valor referente ao último mês completo",
                    'xref': "paper",
                    'yref': "paper"
                }
            ],
            'width': 500, 
            'height': 320
        }
    )

    col2.plotly_chart(fig)

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['Ocorrências de -11Hs Interjornadas'].median() 

    dados_lex_resampled = dados_compilados.resample('M')['Ocorrências de -11Hs Interjornadas'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    dados_metas_11hs = dados_metas_planilha[['Ocorrências de -11Hs Interjornadas']].rename(columns={'Ocorrências de -11Hs Interjornadas': 'meta'})

    meta_value_decimal = dados_metas_11hs['meta'].median()

    meta_value_percent = str(dados_metas_11hs['meta'].median())

    meta_value_percent = meta_value_percent.rstrip('0').rstrip('.') if '.' in meta_value_percent else meta_value_percent

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Ocorrências de -11Hs Interjornadas", 'Ocorrências de -11Hs Interjornadas', f"Meta: {meta_value_percent}", meta_value_decimal, meta_value_decimal))

    value = dados_lex_gauge['Ocorrências de -11Hs Interjornadas'].median()

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Ocorrências de -11Hs Interjornadas", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': meta_value_decimal, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, 100], 'color': '#fab8a3'}, 
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ),
        layout={
            'annotations': [
                {
                    'x': 0.5,
                    'y': -0.25,
                    'showarrow': False,
                    'text': "Valor referente ao último mês completo",
                    'xref': "paper",
                    'yref': "paper"
                }
            ],
            'width': 500, 
            'height': 320
        }
    )

    col2.plotly_chart(fig)

with tab2:

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['OPAV'].median() 

    dados_lex_resampled = dados_compilados.resample('M')['OPAV'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    dados_metas_opav = dados_metas_planilha[['OPAV']].rename(columns={'OPAV': 'meta'})

    meta_value_decimal = dados_metas_opav['meta'].median()

    meta_value_percent = str(dados_metas_opav['meta'].median() * 100)

    meta_value_percent = meta_value_percent.rstrip('0').rstrip('.') if '.' in meta_value_percent else meta_value_percent

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "OPAV", 'OPAV', f"Meta: {meta_value_percent}%", meta_value_decimal, meta_value_decimal))

    value = dados_lex_gauge['OPAV'].median() 

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "OPAV", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': meta_value_decimal, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 1]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, meta_value_decimal], 'color': '#c9f1ac'},
                    {'range': [meta_value_decimal, 1], 'color': '#fab8a3'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ),
        layout={
            'annotations': [
                {
                    'x': 0.5,
                    'y': -0.25,
                    'showarrow': False,
                    'text': "Valor referente ao último mês completo",
                    'xref': "paper",
                    'yref': "paper"
                }
            ],
            'width': 500, 
            'height': 320
        }
    )

    col2.plotly_chart(fig)

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['Programa 5S'].median()  

    dados_lex_resampled = dados_compilados.resample('M')['Programa 5S'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    dados_metas_5s = dados_metas_planilha[['Programa 5S']].rename(columns={'Programa 5S': 'meta'})

    meta_value_decimal = dados_metas_5s['meta'].median() * 10

    meta_value_percent = str(dados_metas_5s['meta'].median() * 10)

    meta_value_percent = meta_value_percent.rstrip('0').rstrip('.') if '.' in meta_value_percent else meta_value_percent

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Programa 5S", 'Programa 5S', f"Meta: {meta_value_percent}%", meta_value_decimal, meta_value_decimal))

    value = dados_lex_gauge['Programa 5S'].median()

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Programa 5S", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': meta_value_decimal, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 10]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, meta_value_decimal], 'color': '#fab8a3'}, 
                    {'range': [meta_value_decimal, 10], 'color': '#c9f1ac'}, 
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ),
        layout={
            'annotations': [
                {
                    'x': 0.5,
                    'y': -0.25,
                    'showarrow': False,
                    'text': "Valor referente ao último mês completo",
                    'xref': "paper",
                    'yref': "paper"
                }
            ],
            'width': 500, 
            'height': 320
        }
    )

    col2.plotly_chart(fig)

loading_message.progress(80, text=text)

with tab3:

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['Produtividade Média'].median()  

    dados_lex_resampled = dados_compilados.resample('M')['Produtividade Média'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    dados_metas_prod = dados_metas_planilha[['Produtividade Média']].rename(columns={'Produtividade Média': 'meta'})

    meta_value_decimal = dados_metas_prod['meta'].median()

    meta_value_percent = str(dados_metas_prod['meta'].median())

    meta_value_percent = meta_value_percent.rstrip('0').rstrip('.') if '.' in meta_value_percent else meta_value_percent

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Produtividade Média", 'Produtividade Média', f"Meta: {meta_value_percent}", meta_value_decimal, meta_value_decimal))

    value = dados_lex_gauge['Produtividade Média'].median()

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Produtividade Média", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': meta_value_decimal, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 1500]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, meta_value_decimal], 'color': '#fab8a3'}, 
                    {'range': [meta_value_decimal, 1500], 'color': '#c9f1ac'}, 
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ),
        layout={
            'annotations': [
                {
                    'x': 0.5,
                    'y': -0.25,
                    'showarrow': False,
                    'text': "Valor referente ao último mês completo",
                    'xref': "paper",
                    'yref': "paper"
                }
            ],

            'width': 500,
            'height': 320
        }
    )
    col2.plotly_chart(fig)


with tab5:

    st.write("  ")
    st.write("  ")

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['Auditoria'].median() 

    dados_lex_resampled = dados_compilados.resample('M')['Auditoria'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    dados_metas_aud = dados_metas_planilha[['Auditoria']].rename(columns={'Auditoria': 'meta'})

    meta_value_decimal = dados_metas_aud['meta'].median()

    meta_value_percent = str(dados_metas_aud['meta'].median())

    meta_value_percent = meta_value_percent.rstrip('0').rstrip('.') if '.' in meta_value_percent else meta_value_percent

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Auditoria", 'Auditoria', f"Meta: {meta_value_percent}", meta_value_decimal, meta_value_decimal))

    value = dados_lex_gauge['Auditoria'].median()  

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Auditoria", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': meta_value_decimal, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 1.2]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, meta_value_decimal], 'color': '#fab8a3'},
                    {'range': [meta_value_decimal, 1.2], 'color': '#c9f1ac'}, 
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ),
        layout={
            'annotations': [
                {
                    'x': 0.5,
                    'y': -0.25,
                    'showarrow': False,
                    'text': "Valor referente ao último mês completo",
                    'xref': "paper",
                    'yref': "paper"
                }
            ],

            'width': 500,
            'height': 320
        }
    )
 
    col2.plotly_chart(fig)

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['Auto avaliação'].median()

    dados_lex_resampled = dados_compilados.resample('M')['Auto avaliação'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    dados_metas_auto = dados_metas_planilha[['Auto avaliação']].rename(columns={'Auto avaliação': 'meta'})

    meta_value_decimal = dados_metas_auto['meta'].median()

    meta_value_percent = str(dados_metas_auto['meta'].median())

    meta_value_percent = meta_value_percent.rstrip('0').rstrip('.') if '.' in meta_value_percent else meta_value_percent

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Auto avaliação", 'Auto avaliação', f"Meta: {meta_value_percent}", meta_value_decimal, meta_value_decimal))

    value = dados_lex_gauge['Auto avaliação'].median()

    fig = go.Figure(

        go.Indicator(
                
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Auto avaliação", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
                delta={'reference': meta_value_decimal, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
                gauge={
                    'axis': {'range': [0, 1.2]},
                    'bar': {'color': '#8fe1ff'},
                    'steps': [
                    {'range': [0, meta_value_decimal], 'color': '#fab8a3'},
                    {'range': [meta_value_decimal, 1.2], 'color': '#c9f1ac'}, 
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': value
                    }
                }
            ),
            layout={
            'annotations': [
                {
                    'x': 0.5,
                    'y': -0.25,
                    'showarrow': False,
                    'text': "Valor referente ao último mês completo",
                    'xref': "paper",
                    'yref': "paper"
                }
            ],

            'width': 500,
            'height': 320
        }

    )

    col2.plotly_chart(fig)


loading_message.progress(100, text=text)
time.sleep(1)
loading_message.empty()

 
