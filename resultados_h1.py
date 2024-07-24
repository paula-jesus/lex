import pandas as pd
from utils import FormatoNumeros, PesoAtingimento
from consts import *
from estilizador import Dataframes
import streamlit as st
import plotly.express as px
import re
import numpy as np
from trat_dataframes import process_data

@st.cache_data(show_spinner=False, ttl=10000000, experimental_allow_widgets=True)
def comparativo_h1(type_abrev):

    if type_abrev == 'Ag':
        type = 'Agência'
        key = 'comparar_bases_ag'
    elif type_abrev == 'XD':
        type = 'Crossdocking'
        key = 'comparar_bases_xd'
    
    _, _, dados_compilados, dados_metas_planilha, _, _, _, detalhamento_comparativo, dados_pesos, pesos_pivot = process_data(type, type_abrev, key)

    dados_compilados = dados_compilados[dados_compilados['Mês'] <= '2024-06']

    month = st.multiselect('Mês', dados_compilados['Mês'].unique(), placeholder='Selecione um ou mais meses')
    if month:
        dados_compilados = dados_compilados[dados_compilados['Mês'].isin(month)]

    dados_metas_planilha.rename(columns={'month': 'Mês', 'routing_code': ROUTING_CODE}, inplace=True)
    dados_compilados.rename(columns={'routing_code': ROUTING_CODE}, inplace=True)
    dados_pesos.rename(columns={'routing_code': ROUTING_CODE}, inplace=True)
    dados_metas_planilha['Mês'] = dados_metas_planilha['Mês'].dt.to_timestamp().dt.strftime('%Y-%m')

    detalhamento = dados_compilados.copy()

    dados_compilados = pd.merge(dados_compilados, dados_metas_planilha, on=[ROUTING_CODE, 'Mês'], how='inner', validate="many_to_many")

    if type_abrev == 'Ag': 
        columns = [OPAV, PRODMEDIA, INVENTARIO, ABS, 
            TREINAMENTO, 
            AUDITORIA, AUTOAVALIACAO, CUSTO, LR, SLA, 
            O2HE, O11INTER]
    if type_abrev == 'XD':
        columns = [OPAV, PRODMEDIA, INVENTARIO, ABS, 
            TREINAMENTO, 
            AUDITORIA, AUTOAVALIACAO, CUSTO, LR, 
            O2HE, O11INTER, PROGRAMA5S]

    for col in columns:
        dados_compilados[col] = dados_compilados[f'{col}_x'] / dados_compilados[f'{col}_y']  

    if type_abrev == 'Ag':
        dados_compilados = dados_compilados.drop(['OPAV_x', 'OPAV_y', 'Produtividade Média_x', 'Produtividade Média_y', 'Inventário_x', 'Inventário_y', 'Absenteísmo_x', 'Absenteísmo_y', 'Treinamentos_x', 'Treinamentos_y', 'Auditoria_x', 'Auditoria_y', 'Auto avaliação_x', 'Auto avaliação_y', 'Custo por Pacote_x', 'Custo por Pacote_y', 'Loss Rate_x', 'Loss Rate_y', 'SLA_x', 'SLA_y', 'Ocorrências de +2HE_x', 'Ocorrências de +2HE_y', 'Ocorrências de Interjornadas_x', 'Ocorrências de Interjornadas_y'], axis=1)

    if type_abrev == 'XD':
        dados_compilados = dados_compilados.drop(['OPAV_x', 'OPAV_y', 'Produtividade Média_x', 'Produtividade Média_y', 'Inventário_x', 'Inventário_y', 'Absenteísmo_x', 'Absenteísmo_y', 'Treinamentos_x', 'Treinamentos_y', 'Auditoria_x', 'Auditoria_y', 'Auto avaliação_x', 'Auto avaliação_y', 'Custo por Pacote_x', 'Custo por Pacote_y', 'Loss Rate_x', 'Loss Rate_y', 'Ocorrências de +2HE_x', 'Ocorrências de +2HE_y', 'Ocorrências de Interjornadas_x', 'Ocorrências de Interjornadas_y', 'Programa 5S_x', 'Programa 5S_y'], axis=1)    

    dados_compilados = pd.merge(dados_compilados, dados_pesos, on=[ROUTING_CODE], how='inner', validate="many_to_many")

    dados_compilados[OPAV] = np.where(dados_compilados['OPAV_x'] > 1, 0, dados_compilados['OPAV_y'])
    dados_compilados[O11INTER] = np.where(dados_compilados['Ocorrências de Interjornadas_x'] > 1, 0, dados_compilados['Ocorrências de Interjornadas_y'])
    dados_compilados[ABS] = np.where(dados_compilados['Absenteísmo_x'] > 1, 0, dados_compilados['Absenteísmo_y'])
    dados_compilados[CUSTO] = np.where(dados_compilados['Custo por Pacote_x'] > 1, 0, dados_compilados['Custo por Pacote_y'])
    dados_compilados[LR] = np.where(dados_compilados['Loss Rate_x'] > 1, 0, dados_compilados['Loss Rate_y'])
    dados_compilados[O2HE] = np.where(dados_compilados['Ocorrências de +2HE_x'] > 1, 0, dados_compilados['Ocorrências de +2HE_y'])
    dados_compilados[TREINAMENTO] = np.where(dados_compilados['Treinamentos_x'] > 1, dados_compilados['Treinamentos_y'], dados_compilados['Treinamentos_x'] * dados_compilados['Treinamentos_y'])
    dados_compilados[AUDITORIA] = np.where(dados_compilados['Auditoria_x'] > 1, dados_compilados['Auditoria_y'], dados_compilados['Auditoria_x'] * dados_compilados['Auditoria_y'])
    dados_compilados[AUTOAVALIACAO] = np.where(dados_compilados['Auto avaliação_x'] > 1, dados_compilados['Auto avaliação_y'], dados_compilados['Auto avaliação_x'] * dados_compilados['Auto avaliação_y'])
    dados_compilados[INVENTARIO] = np.where(dados_compilados['Inventário_x'] > 1, dados_compilados['Inventário_y'], dados_compilados['Inventário_x'] * dados_compilados['Inventário_y'])
    dados_compilados[PRODMEDIA] = np.where(dados_compilados['Produtividade Média_x'] > 1, dados_compilados['Produtividade Média_y'], dados_compilados['Produtividade Média_x'] * dados_compilados['Produtividade Média_y'])
    if type_abrev == 'XD':
        dados_compilados[PROGRAMA5S] = np.where(dados_compilados['Programa 5S_x'] > 1, dados_compilados['Programa 5S_y'], dados_compilados['Programa 5S_x'] * dados_compilados['Programa 5S_y'])
    if type_abrev == 'Ag': 
                dados_compilados[SLA] = np.where(dados_compilados['SLA_x'] > 1, dados_compilados['SLA_y'], dados_compilados['SLA_x'] * dados_compilados['SLA_y'])        

    if type_abrev == 'Ag':
        dados_compilados = dados_compilados[[ROUTING_CODE, 'Mês', OPAV, PRODMEDIA, INVENTARIO, ABS, TREINAMENTO, AUDITORIA, AUTOAVALIACAO, CUSTO, LR, SLA, O2HE, O11INTER]]
    if type_abrev == 'XD':
        dados_compilados = dados_compilados[[ROUTING_CODE, 'Mês', OPAV, PRODMEDIA, INVENTARIO, ABS, TREINAMENTO, AUDITORIA, AUTOAVALIACAO, CUSTO, LR, O2HE, O11INTER, PROGRAMA5S]]   

    dados_compilados = dados_compilados.pivot_table(columns=[ROUTING_CODE, 'Mês'], aggfunc='median')

    pesos_pivot.set_index('index', inplace=True)

    dados_compilados['Peso'] = dados_compilados.index.map(pesos_pivot.iloc[:, 0])

    totals = dados_compilados.sum()
    dados_compilados.loc['Atingimento Total'] = totals

    dados_compilados.iloc[:, :-1] = dados_compilados.iloc[:, :-1].applymap(lambda x: f'{x:.0f}%' if np.isfinite(x) and x == int(x) else f'{x:.2f}%' if np.isfinite(x) else '')
    dados_compilados['Peso'] = dados_compilados['Peso'].apply(lambda x: f'{x:.0f}' if np.isfinite(x) and x == int(x) else f'{x:.2f}' if np.isfinite(x) else '')

    dados_compilados = dados_compilados.fillna('')

    teste = dados_compilados.copy()

    if type_abrev == 'XD':
        order = [ABS, O2HE, O11INTER, TREINAMENTO, PROGRAMA5S, OPAV, INVENTARIO, PRODMEDIA, LR, CUSTO, AUTOAVALIACAO, AUDITORIA, 'Atingimento Total'] 
    if type_abrev == 'Ag':
        order = [ABS, O2HE, O11INTER, TREINAMENTO, OPAV, INVENTARIO, PRODMEDIA, SLA, LR, CUSTO, AUTOAVALIACAO, AUDITORIA, 'Atingimento Total']

    dados_compilados = dados_compilados.reindex(order)    

    dados_compilados_styled = dados_compilados.style.apply(PesoAtingimento.color_achievement, type='Peso', axis=1)

    detalhamento = detalhamento.pivot_table(columns=[ROUTING_CODE,'Mês'], aggfunc='median')

    if type_abrev == 'XD':
        row_labels_percent = [OPAV, ABS,AUDITORIA,AUTOAVALIACAO, INVENTARIO, TREINAMENTO, PROGRAMA5S]
        row_labels = [PROGRAMA5S,O2HE,O11INTER,PRODMEDIA]

    if type_abrev == 'Ag':
        row_labels_percent = [OPAV, ABS,AUDITORIA,AUTOAVALIACAO, INVENTARIO, TREINAMENTO, SLA]
        row_labels = [O2HE,O11INTER,PRODMEDIA]

    row_labels_finance = [CUSTO, LR]

    detalhamento = FormatoNumeros.format_rows(detalhamento, row_labels_percent, FormatoNumeros.format_func_percent)
    detalhamento = FormatoNumeros.format_rows(detalhamento, row_labels, FormatoNumeros.format_func)
    detalhamento = FormatoNumeros.format_rows(detalhamento, row_labels_finance, FormatoNumeros.format_func_finance, key='detalhamento')

    detalhamento = detalhamento.fillna('')

    comparativo_pesos_transformado = teste.transpose()
    comparativo_pesos_transformado.reset_index(inplace=True)
    detalhamento_comparativo.drop(columns='Peso', inplace=True)
    detalhamento_comparativo.drop(columns='Meta', inplace=True)
    detalhamento_comparativo_transformado = detalhamento.transpose()
    detalhamento_comparativo_transformado.reset_index(inplace=True)

    last_complete_month = comparativo_pesos_transformado['Mês'].max()
    comparativo_pesos_transformado = comparativo_pesos_transformado[comparativo_pesos_transformado['Mês'] == last_complete_month]
    detalhamento_comparativo_transformado = detalhamento_comparativo_transformado[detalhamento_comparativo_transformado['Mês'] == last_complete_month]

    comparativo_pesos_transformado['Atingimento Total'] = comparativo_pesos_transformado['Atingimento Total'].str.replace('%', '').astype(float)

    detalhamento_comparativo_transformado[LR] = detalhamento_comparativo_transformado[LR].apply(lambda x: re.sub('\s*R\$ \s*', '', x)).astype(float)
    detalhamento_comparativo_transformado[CUSTO] = detalhamento_comparativo_transformado[CUSTO].apply(lambda x: re.sub('\s*R\$ \s*', '', x))

    comparativo_pesos_html = Dataframes.generate_html(dados_compilados_styled)
    st.subheader('Atingimeto com pesos')
    st.write(comparativo_pesos_html, unsafe_allow_html=True)
    dados_compilados = dados_compilados.to_csv().encode('utf-8')
    st.download_button(label='Download', data= dados_compilados, file_name='Resultados_BSC.csv', key=(key + 'download'), mime='csv')
    st.divider()
    st.subheader('Detalhamento dos resultados')
    detalhamento_comparativo_html = Dataframes.generate_html(detalhamento)
    st.write(detalhamento_comparativo_html, unsafe_allow_html=True)
    detalhamento_comparativo = detalhamento_comparativo.to_csv().encode('utf-8')
    st.download_button(label='Download', data= detalhamento_comparativo, file_name='Detalhamento_BSC.csv', key=(key + 'download2'), mime='csv')
    st.divider()

    st.write('Gráficos referentes ao último mês completo')

    comparativo_pesos_transformado = comparativo_pesos_transformado.sort_values(by='Atingimento Total', ascending=False)
    fig = px.line(comparativo_pesos_transformado, x=ROUTING_CODE, y='Atingimento Total', title='Atingimento Total', labels={'index': ROUTING_CODE, 'Atingimento Total': 'Atingimento Total'}, range_y=[0,100])
    fig.update_traces(mode='markers+lines')
    st.plotly_chart(fig)

    pessoas = detalhamento_comparativo_transformado.melt(id_vars=ROUTING_CODE, value_vars=[ABS, TREINAMENTO, O2HE, O11INTER])
    fig = px.bar(pessoas, barmode='group', x='variable', y='value', color=ROUTING_CODE, title='Pilar de Pessoas', labels={'variable': 'Indicador', 'value': 'Atingimento'})
    st.plotly_chart(fig)

    if type_abrev == 'XD':
        qualidade = detalhamento_comparativo_transformado.melt(id_vars=ROUTING_CODE, value_vars=[OPAV, INVENTARIO, PROGRAMA5S])
    elif type_abrev == 'Ag':
        qualidade = detalhamento_comparativo_transformado.melt(id_vars=ROUTING_CODE, value_vars=[OPAV, INVENTARIO, SLA])
    fig = px.bar(qualidade, barmode='group', x='variable', y='value', color=ROUTING_CODE, title='Pilar de Qualidade', labels={'variable': 'Indicador', 'value': 'Atingimento'})
    st.plotly_chart(fig)

    entrega = detalhamento_comparativo_transformado.melt(id_vars=ROUTING_CODE, value_vars=[PRODMEDIA])
    fig = px.bar(entrega, barmode='group', x='variable', y='value', color=ROUTING_CODE, title='Pilar de Entrega', labels={'variable': 'Indicador', 'value': 'Atingimento'})
    st.plotly_chart(fig)

    Financeiro = detalhamento_comparativo_transformado.melt(id_vars=ROUTING_CODE, value_vars=[CUSTO, LR])
    fig = px.bar(Financeiro, barmode='group', x='variable', y='value', color=ROUTING_CODE, title='Pilar Financeiro', labels={'variable': 'Indicador', 'value': 'Atingimento'})
    st.plotly_chart(fig)

    auditoria = detalhamento_comparativo_transformado.melt(id_vars=ROUTING_CODE, value_vars=[AUDITORIA, AUTOAVALIACAO])
    fig = px.bar(auditoria, barmode='group', x='variable', y='value', color=ROUTING_CODE, title='Pilar de Auditoria', labels={'variable': 'Indicador', 'value': 'Atingimento'})
    st.plotly_chart(fig)
