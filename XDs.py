import streamlit as st
import pandas as pd
from utils import EstilizarPagina, GerarTabela, gerar_tabela_sheets, create_area_plot, filter_by_multiselect
from estilizador import DataframeStyler, PageStyler
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

estilizador = EstilizarPagina()
estilizador.set_page_config()

text = "Dados carregando... Duração entre 1 e 5 minutos ⌛"
loading_message = st.empty()

last_month = pd.to_datetime('today') - pd.DateOffset(months=1)

tabela = GerarTabela()
dados_looker = tabela.gerar_dados_lex()
dados_planilha = gerar_tabela_sheets('1wQs6k5eGKASNxSMYcfHwP5HK7PSEDo0t_uzLYke_u3s','fonte_oficial')
dados_metas = gerar_tabela_sheets('1htP_m0eMy7pMxvB4EJIMIPfspzHZv66pH5cpLxjprMU','metas')

mask = dados_looker['type_dc'] == 'Crossdocking'
dados_looker = dados_looker[mask]

mask = dados_metas['type_dc'] == 'Crossdocking'
dados_metas = dados_metas[mask]

dados_planilha = dados_planilha.drop('#', axis=1)

loading_message.progress(0, text=text)

dados_looker['month'] = pd.to_datetime(dados_looker['month'])
dados_looker['month'] = dados_looker['month'].dt.strftime('%Y-%m')
mask = dados_looker['month'] >= '2023-12'
dados_looker = dados_looker[mask]

for column in ['Auditoria', 'Auto avaliação','Programa 5S']:
    dados_planilha[column] = pd.to_numeric(dados_planilha[column], errors='coerce')

dados_compilados = pd.merge(dados_looker, dados_planilha, on=['month', 'routing_code'], how='left')

#Filtros

dados_compilados = filter_by_multiselect(dados_compilados, "month", "Mês")

dados_compilados = filter_by_multiselect(dados_compilados, "routing_code", "Routing Code")

dados_compilados.rename(columns={'month': 'Mês', 'opav': 'OPAV', 'produtividade_media': 'Produtividade Média', 'loss_rate': 'Loss Rate', 'sla':'SLA','Auto avaliacao':'Auto avaliação','backlog':'Backlog','two_hrs':'Ocorrências de +2HE','abs':'Absenteísmo','cnt_interjornada':'Ocorrências de -11Hs Interjornadas'}, inplace=True)

dados_lex_gauge = dados_compilados[dados_compilados['Mês'] == last_month.strftime('%Y-%m')]

dados_tabela_pivtada = dados_compilados.copy()

# st.write(dados_tabela_pivtada)

dados_tabela_pivtada.rename(columns={'Mês': 'KPIs'}, inplace=True)

pivot_table = dados_tabela_pivtada.pivot_table(columns='KPIs', aggfunc='median')
    
pivot_table = pivot_table.reset_index()

dados_mergeados_meta = pd.merge(pivot_table, dados_metas, left_on='index', right_on='KPI', how='right')

dados_mergeados_meta.set_index('KPI', inplace=True)

dados_mergeados_meta.index.name = None

tabela_com_pesos = dados_mergeados_meta.copy()

dados_mergeados_meta = dados_mergeados_meta.drop(['type_dc', 'peso', 'pilar', 'index'], axis=1)

pivot_table_reset = dados_mergeados_meta.fillna('')

pivot_table_reset.rename(columns={'Mês': 'KPIs'}, inplace=True)

pivot_table_reset.loc[['OPAV', 'SLA', 'Absenteísmo', 'Loss Rate','Auditoria','Auto avaliação']] *= 100

def format_row_with_percent(row):
    return row.apply(lambda x: f'{x:.0f}%' if isinstance(x, (int, float)) and np.isfinite(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (int, float)) else x)

row_labels = ['OPAV', 'SLA', 'Absenteísmo', 'Loss Rate','Auditoria','Auto avaliação']  
pivot_table_reset.loc[row_labels] = pivot_table_reset.loc[row_labels].apply(format_row_with_percent, axis=1)

def format_row(row):
    return row.apply(lambda x: f'{x:.0f}' if isinstance(x, (int, float)) and np.isfinite(x) and x == int(x) else f'{x:.2f}' if isinstance(x, (int, float)) and np.isfinite(x) else x)

row_labels = ['Programa 5S','Ocorrências de +2HE','Ocorrências de -11Hs Interjornadas','Produtividade Média']  
pivot_table_reset.loc[row_labels] = pivot_table_reset.loc[row_labels].apply(format_row, axis=1)

# def color_based_on_row(row): 
#     meta = row['Meta'] 
#     row_name = row.name 
#     if row_name in ('Absenteísmo','OPAV','Loss Rate','Auditoria','Ocorrências de +2HE','Ocorrências de -11Hs Interjornadas'): 
#         return ['color: red' if val > meta else 'color: black' for val in row] 
#     else: 
#         return ['color: red' if val < meta else 'color: black' for val in row]

# styled_df = pivot_table_reset.style.apply(color_based_on_row, axis=1)

rendered_table = pivot_table_reset.to_html()
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

else:

    def atingimento_com_peso(row):
        meta = row['Meta']
        peso = row['peso']
        row_name = row.name
        if row_name in ('Ocorrências de +2HE','Ocorrências de -11Hs Interjornadas','Absenteísmo','Backlog','Loss Rate','OPAV'):
            return pd.Series([peso if isinstance(val, (int, float)) and val <= meta else 0 if isinstance(val, (int, float)) else None for val in row], index=row.index)
        else:
            return pd.Series([peso if isinstance(val, (int, float)) and val >= meta else 0 if isinstance(val, (int, float)) else None for val in row], index=row.index)
        
    tabela_com_pesos['Meta'] = pd.to_numeric(tabela_com_pesos['Meta'], errors='coerce')

    agrupado_por_pilar = tabela_com_pesos.groupby('pilar').sum()

    st.write(agrupado_por_pilar)

    tabela_com_pesos = tabela_com_pesos.drop(['type_dc', 'pilar', 'index'], axis=1)

    tabela_com_pesos.dropna(subset=['Meta'], inplace=True)

    tabela_com_pesos_styled = tabela_com_pesos.apply(atingimento_com_peso, axis=1)

    tabela_com_pesos_styled = tabela_com_pesos_styled.fillna(0)

    totals = tabela_com_pesos_styled.sum()

    tabela_com_pesos_styled.loc['Atingimento Total'] = totals

    tabela_com_pesos_styled = tabela_com_pesos_styled.drop(['Meta', 'peso'], axis=1)

    tabela_com_pesos_styled = tabela_com_pesos_styled.applymap(lambda x: f'{x:.0f}%'.format(x))

    rendered_table = tabela_com_pesos_styled.to_html()
    centered_table = f"""
    <div style="display: flex; justify-content: center;">
    <div style="max-height: 500px; overflow-y: auto;">
            {rendered_table}
    """

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

    value = dados_compilados['Absenteísmo'].median()
    
    dados_lex_resampled = dados_compilados.resample('M')['Absenteísmo'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Absenteísmo", 'Absenteísmo', "Meta: 3%", 0.03, 0.03))

    value = dados_lex_gauge['Absenteísmo'].median()

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Absenteísmo", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': 0.03, 'increasing': {'color': "red"}, 'decreasing': {'color': "black"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 0.1]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, 0.03], 'color': '#c9f1ac'},  
                    {'range': [0.03, 0.1], 'color': '#fab8a3'},  
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

    chart = create_area_plot(dados_lex_resampled, "Ocorrências de +2HE", 'Ocorrências de +2HE', "Meta: 0", 0, 0)

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

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Ocorrências de -11Hs Interjornadas", 'Ocorrências de -11Hs Interjornadas', "Meta: 0", 0, 0))

    value = dados_lex_gauge['Ocorrências de -11Hs Interjornadas'].median()

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Ocorrências de -11Hs Interjornadas", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': 0, 'increasing': {'color': "red"}, 'decreasing': {'color': "black"}},
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

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "OPAV", 'OPAV', "Meta: 36%", 0.36, 0.36))

    value = dados_lex_gauge['OPAV'].median() 

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "OPAV", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': 0.36, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 1]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, 0.36], 'color': '#c9f1ac'},
                    {'range': [0.36, 1], 'color': '#fab8a3'}
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

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Programa 5S", 'Programa 5S', "Meta: 8", 8, 8))

    value = dados_lex_gauge['Programa 5S'].median()

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Programa 5S", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': 8, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 10]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, 8], 'color': '#fab8a3'}, 
                    {'range': [8, 10], 'color': '#c9f1ac'}, 
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


with tab3:

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['SLA'].median()

    dados_lex_resampled = dados_compilados.resample('M')['SLA'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "SLA", 'SLA', "Meta: 97%", 0.97, 0.97))

    value = dados_lex_gauge['SLA'].median() 

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "SLA", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': 0.97, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 1]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, 0.97], 'color': '#fab8a3'},
                    {'range': [0.97, 1], 'color': '#c9f1ac'}, 
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

    value = dados_compilados['Produtividade Média'].median()  

    dados_lex_resampled = dados_compilados.resample('M')['Produtividade Média'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Produtividade Média", 'Produtividade Média', "Meta: 1100", 1100, 1100))

    value = dados_lex_gauge['Produtividade Média'].median()

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Produtividade Média", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': 1100, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 1500]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, 1100], 'color': '#fab8a3'}, 
                    {'range': [1100, 1500], 'color': '#c9f1ac'}, 
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

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Auditoria", 'Auditoria', "Meta: 1", 1, 1))

    value = dados_lex_gauge['Auditoria'].median()  

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Auditoria", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
            delta={'reference': 1, 'increasing': {'color': "black"}, 'decreasing': {'color': "red"}},
            number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 1.2]},
                'bar': {'color': '#8fe1ff'},
                'steps': [
                    {'range': [0, 1], 'color': '#fab8a3'},
                    {'range': [1, 1.2], 'color': '#c9f1ac'}, 
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ),
        layout={'width': 500, 'height': 320}
    )
 
    col2.plotly_chart(fig)

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['Auto avaliação'].median()

    dados_lex_resampled = dados_compilados.resample('M')['Auto avaliação'].median().reset_index()

    dados_lex_resampled['Mês'] = dados_lex_resampled['Mês'].dt.strftime('%b %Y')

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Auto avaliação", 'Auto avaliação', "Meta: 1", 1, 1))

    value = dados_lex_gauge['Auto avaliação'].median()

    fig = go.Figure(

        go.Indicator(
                
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Auto avaliação", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
                delta={'reference': 1, 'increasing': {'color': "RebeccaPurple"}, 'decreasing': {'color': "black"}},
                number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
                gauge={
                    'axis': {'range': [0, 1.2]},
                    'bar': {'color': '#8fe1ff'},
                    'steps': [
                    {'range': [0, 1], 'color': '#fab8a3'},
                    {'range': [1, 1.2], 'color': '#c9f1ac'}, 
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': value
                    }
                }
            ),
            layout={'width': 500, 'height': 320}

    )

    col2.plotly_chart(fig)


loading_message.empty()

 
