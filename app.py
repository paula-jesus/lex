import streamlit as st
import pandas as pd
from utils import EstilizarPagina, GerarTabela, gerar_tabela_sheets, create_area_plot, filter_by_multiselect
from estilizador import DataframeStyler, PageStyler
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

estilizador = EstilizarPagina()
estilizador.set_page_config()

last_month = pd.to_datetime('today') - pd.DateOffset(months=1)

tabela = GerarTabela()
dados_looker = tabela.gerar_dados_lex()
dados_planilha = gerar_tabela_sheets()

dados_planilha = dados_planilha.drop('#', axis=1)

text = "Dados carregando... Duração entre 1 e 5 minutos ⌛"
loading_message = st.empty()

loading_message.progress(0, text=text)

dados_looker['month'] = pd.to_datetime(dados_looker['month'])
dados_looker['month'] = dados_looker['month'].dt.strftime('%Y-%m')

for column in ['Auditoria', 'Autoavaliação','Programa 5S']:
    dados_planilha[column] = pd.to_numeric(dados_planilha[column], errors='coerce')

dados_compilados = pd.merge(dados_looker, dados_planilha, on=['month', 'routing_code'], how='left')

#Filtros

dados_compilados = filter_by_multiselect(dados_compilados, "type_dc", "Tipo de DC")

dados_compilados = filter_by_multiselect(dados_compilados, "month", "Mês")

dados_compilados = filter_by_multiselect(dados_compilados, "routing_code", "Routing Code")

dados_compilados.rename(columns={'month': 'Mês', 'opav': 'OPAV', 'produtividade_media': 'Produtividade Média', 'loss_rate': 'Loss Rate', 'sla':'SLA','autoavaliacao':'Autoavaliação','backlog':'Backlog','two_hrs':'Ocorrências de +2HE','abs':'Absenteísmo','cnt_interjornada':'Ocorrências de -11Hs Interjornadas'}, inplace=True)

dados_lex_gauge = dados_compilados[dados_compilados['Mês'] == last_month.strftime('%Y-%m')]

dados_tabela_pivtada = dados_compilados.copy()

dados_tabela_pivtada.rename(columns={'Mês': 'KPIs'}, inplace=True)

pivot_table = dados_tabela_pivtada.pivot_table(columns='KPIs', aggfunc='median')

# Define a function that returns the goal based on the column name
def get_goal(row):
    if row.name == 'OPAV':
        return 0.36
    elif row.name == 'Programa 5S':
        return 8
    elif row.name == 'SLA':
        return 0.97
    elif row.name == 'Produtividade Média':
        return 1100
    elif row.name == 'Loss Rate':
        return 0.20
    elif row.name == 'Auditoria':
        return 1
    elif row.name == 'Autoavaliação':
        return 1
    elif row.name == 'Ocorrências de +2HE':
        return 0
    elif row.name == 'Ocorrências de -11Hs Interjornadas':
        return 0
    elif row.name == 'Absenteísmo': 
        return 0.03   
    elif row.name == 'Backlog':
        return 0.1        
    else:
        return None 
    
def peso(row):
    if row.name == 'OPAV':
        return 3
    elif row.name == 'Programa 5S':
        return 3
    elif row.name == 'SLA':
        return 3
    elif row.name == 'Produtividade Média':
        return 3
    elif row.name == 'Loss Rate':
        return 3
    elif row.name == 'Auditoria':
        return 65
    elif row.name == 'Autoavaliação':
        return 1
    elif row.name == 'Ocorrências de +2HE':
        return 3
    elif row.name == 'Ocorrências de -11Hs Interjornadas':
        return 1
    elif row.name == 'Absenteísmo': 
        return 1   
    elif row.name == 'Backlog':
        return 3        
    else:
        return None  
    
pivot_table['Meta'] = pivot_table.apply(get_goal, axis=1)

# Get a list of the column names
cols = list(pivot_table.columns)

# Remove 'goal' from the list
cols.remove('Meta')

# Insert 'goal' at the second position
cols.insert(0, 'Meta')

# Reorder the DataFrame
pivot_table_reset = pivot_table[cols]

tabela_com_pesos = pivot_table_reset.copy()

pivot_table_reset.rename(columns={'Mês': 'KPIs'}, inplace=True)

pivot_table_reset.loc[['OPAV', 'SLA', 'Absenteísmo', 'Loss Rate','Backlog','Auditoria','Autoavaliação']] *= 100

def format_row_with_percent(row):
    return row.apply(lambda x: f'{x:.0f}%' if np.isfinite(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (int, float)) else x)

row_labels = ['OPAV', 'SLA', 'Absenteísmo', 'Loss Rate','Backlog','Auditoria','Autoavaliação']  
pivot_table_reset.loc[row_labels] = pivot_table_reset.loc[row_labels].apply(format_row_with_percent, axis=1)

def format_row(row):
    return row.apply(lambda x: f'{x:.0f}' if np.isfinite(x) and x == int(x) else f'{x:.2f}' if isinstance(x, (int, float)) else x)

row_labels = ['Programa 5S','Ocorrências de +2HE','Ocorrências de -11Hs Interjornadas','Produtividade Média']  
pivot_table_reset.loc[row_labels] = pivot_table_reset.loc[row_labels].apply(format_row, axis=1)

def color_based_on_row(row): 
    meta = row['Meta'] 
    row_name = row.name 
    if row_name in ('Absenteísmo','OPAV'): 
        return ['color: red' if val > meta else 'color: black' for val in row] # elif row_name == 2: # Replace 2 with the actual integer for 'SLA' # return ['color: green' if val > meta else 'color: black' for val in row] 
    else: return ['color: red' if val < meta else 'color: black' for val in row]

    
styled_df = pivot_table_reset.style.apply(color_based_on_row, axis=1)

rendered_table = styled_df.to_html()
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

tabela_com_pesos['Peso'] = tabela_com_pesos.apply(peso, axis=1)

def atingimento_com_peso(row):
    meta = row['Meta']
    peso = row['Peso']
    row_name = row.name
    if row_name in ('Ocorrências de +2HE','Ocorrências de -11Hs Interjornadas','Absenteísmo','Backlog','Loss Rate','OPAV'):
        return pd.Series([peso if val <= meta else 0 for val in row if isinstance(val, (int, float))], index=row.index)
    else:
        return pd.Series([peso if val >= meta else 0 for val in row if isinstance(val, (int, float))], index=row.index)

tabela_com_pesos_styled = tabela_com_pesos.apply(atingimento_com_peso, axis=1)

totals = tabela_com_pesos_styled.sum()

tabela_com_pesos_styled.loc['Atingimento Total'] = totals

tabela_com_pesos_styled = tabela_com_pesos_styled.drop(['Meta', 'Peso'], axis=1)

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

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Pessoas","Qualidade","Entrega", "Financeiro", "Auditoria"])

with tab1:

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['Absenteísmo'].median()  # or any other aggregation

    # Convert the 'Mês' column to datetime
    dados_compilados['Mês'] = pd.to_datetime(dados_compilados['Mês'])

    # Resample by month and calculate the median of 'Absenteísmo'
    dados_lex_resampled = dados_compilados.resample('M', on='Mês')['Absenteísmo'].median().reset_index()

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Absenteísmo", 'Absenteísmo', "Meta: 3%", 0.03, 0.03))

    value = dados_lex_gauge['Absenteísmo'].median()  # or any other aggregation

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
                    {'range': [0, 0.03], 'color': '#c9f1ac'},  # Green
                    {'range': [0.03, 0.1], 'color': '#fab8a3'},  # Red
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

    value = dados_compilados['Ocorrências de +2HE'].median()  # or any other aggregation

    # Convert the 'Mês' column to datetime
    dados_compilados['Mês'] = pd.to_datetime(dados_compilados['Mês'])

    # Resample by month and calculate the median of 'Ocorrências de +2HE'
    dados_lex_resampled = dados_compilados.resample('M', on='Mês')['Ocorrências de +2HE'].median().reset_index()

    # Call the function with the required parameters
    chart = create_area_plot(dados_lex_resampled, "Ocorrências de +2HE", 'Ocorrências de +2HE', "Meta: 0", 0, 0)

    # Display the chart
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

    value = dados_compilados['Ocorrências de -11Hs Interjornadas'].median()  # or any other aggregation

    # Convert the 'Mês' column to datetime
    dados_compilados['Mês'] = pd.to_datetime(dados_compilados['Mês'])

    # Resample by month and calculate the median of 'Ocorrências de -11Hs Interjornadas'
    dados_lex_resampled = dados_compilados.resample('M', on='Mês')['Ocorrências de -11Hs Interjornadas'].median().reset_index()

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Ocorrências de -11Hs Interjornadas", 'Ocorrências de -11Hs Interjornadas', "Meta: 0", 0, 0))

    value = dados_lex_gauge['Ocorrências de -11Hs Interjornadas'].median()  # or any other aggregation

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

with tab2:

    col1, col2 = st.columns([1.1, 1])

    value = dados_compilados['OPAV'].median()  # or any other aggregation

    # Convert the 'Mês' column to datetime
    dados_compilados['Mês'] = pd.to_datetime(dados_compilados['Mês'])

    # Resample by month and calculate the median of 'OPAV'
    dados_lex_resampled = dados_compilados.resample('M', on='Mês')['OPAV'].median().reset_index()

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "OPAV", 'OPAV', "Meta: 36%", 0.36, 0.36))

    value = dados_lex_gauge['OPAV'].median()  # or any other aggregation

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
                    # {'range': [0.18, 0.36], 'color': '#fafbbc'},
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

    value = dados_compilados['Programa 5S'].median()  # or any other aggregation

    # Convert the 'Mês' column to datetime
    dados_compilados['Mês'] = pd.to_datetime(dados_compilados['Mês'])

    dados_lex_resampled = dados_compilados.resample('M', on='Mês')['Programa 5S'].median().reset_index()

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

    dados_lex_resampled = dados_compilados.resample('M', on='Mês')['SLA'].median().reset_index()

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

    dados_lex_resampled = dados_compilados.resample('M', on='Mês')['Produtividade Média'].median().reset_index()

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

    # Convert the 'Mês' column to datetime
    dados_compilados['Mês'] = pd.to_datetime(dados_compilados['Mês'])

    # Resample by month and calculate the median of 'Auditoria'
    dados_lex_resampled = dados_compilados.resample('M', on='Mês')['Auditoria'].median().reset_index()

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

    value = dados_compilados['Autoavaliação'].median()  # or any other aggregation

    # Convert the 'Mês' column to datetime
    dados_compilados['Mês'] = pd.to_datetime(dados_compilados['Mês'])

    # Resample by month and calculate the median of 'Autoavaliação'
    dados_lex_resampled = dados_compilados.resample('M', on='Mês')['Autoavaliação'].median().reset_index()

    col1.plotly_chart(create_area_plot(dados_lex_resampled, "Autoavaliação", 'Autoavaliação', "Meta: 1", 1, 1))

    value = dados_lex_gauge['Autoavaliação'].median()  # or any other aggregation

    fig = go.Figure(

        go.Indicator(
                
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Autoavaliação", 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
                delta={'reference': 1, 'increasing': {'color': "RebeccaPurple"}, 'decreasing': {'color': "black"}},
                number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
                gauge={
                    'axis': {'range': [0, 1.2]},
                    'bar': {'color': '#8fe1ff'},
                    'steps': [
                    {'range': [0, 1], 'color': '#fab8a3'},  # Red
                    {'range': [1, 1.2], 'color': '#c9f1ac'},  # Light yellow
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

    col2.plotly_chart(fig)


loading_message.empty()

