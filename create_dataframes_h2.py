import streamlit as st
import pandas as pd
from utils import PesoAtingimento, Ajustes_tabelas, CalcularPesos
from consts import *
import streamlit as st
import numpy as np

def create_tables(type, visao=None, key=None):

    resultados, pesos, metas = Ajustes_tabelas.ajustes_iniciais(type)

    if visao != 'comparativo':
        routing_code = st.sidebar.multiselect('Selecione o routing code', resultados[ROUTING_CODE].unique(), key=key)
        if routing_code:
            resultados = resultados[resultados[ROUTING_CODE].isin(routing_code)]

    if visao == 'comparativo':
        month = st.multiselect('Selecione o mês', resultados[MES].unique(), key=key)
        routing_code = st.multiselect('Selecione o routing code', resultados[ROUTING_CODE].unique())
        if month:
            resultados = resultados[resultados[MES].isin(month)]
        if routing_code:
            resultados = resultados[resultados[ROUTING_CODE].isin(routing_code)]

    resultados['KPI'] = resultados[MES]
    resultados_geral = resultados.pivot_table(columns='KPI', aggfunc='median')
    resultados_comparativo = resultados.pivot_table(columns=[ROUTING_CODE,MES], aggfunc='median')

    pesos_nomeado = Ajustes_tabelas.rename_columns_before_merge(pesos, 'peso', [ROUTING_CODE, MES])
    metas_nomeado = Ajustes_tabelas.rename_columns_before_merge(metas, 'meta', [ROUTING_CODE, MES])
    resultados_nomeado = Ajustes_tabelas.rename_columns_before_merge(resultados, 'resultado', [ROUTING_CODE, MES])

    resultados_com_peso_meta = pd.merge(resultados_nomeado, metas_nomeado, on=[ROUTING_CODE, MES], how='left')
    resultados_com_peso_meta = pd.merge(resultados_com_peso_meta, pesos_nomeado, on=[ROUTING_CODE, MES], how='left')

    if type == 'XD':
        columns = [SLA,PART_TREN_LOGGERS, PART_TREN_LIDERES, APROV_TREN_LOGGERS, APROV_TREN_LIDERES, CUMPR_ROT_QUALIDADE, ATING_AUDITORIA, 'Programa 5S  [XD]', CONFORMIDADE]
    if type == 'Ag':
        columns = [SLA,PART_TREN_LOGGERS, PART_TREN_LIDERES, APROV_TREN_LOGGERS, APROV_TREN_LIDERES, CUMPR_ROT_QUALIDADE, ATING_AUDITORIA, 'IQR Carro', 'IQR Moto']
    CalcularPesos.calculate_columns(resultados_com_peso_meta, columns)

    columns = [ABS, OPAV]
    CalcularPesos.calculate_columns_baixo_melhor(resultados_com_peso_meta, columns)

    if type == 'XD':
        bsc = resultados_com_peso_meta[[ROUTING_CODE, MES, SLA, ABS, OPAV, PART_TREN_LOGGERS, PART_TREN_LIDERES, APROV_TREN_LOGGERS, APROV_TREN_LIDERES, CUMPR_ROT_QUALIDADE, ATING_AUDITORIA, 'Programa 5S  [XD]', CONFORMIDADE]]
    if type == 'Ag':
        bsc = resultados_com_peso_meta[[ROUTING_CODE, MES, SLA, ABS, OPAV, PART_TREN_LOGGERS, PART_TREN_LIDERES, APROV_TREN_LOGGERS, APROV_TREN_LIDERES, CUMPR_ROT_QUALIDADE, ATING_AUDITORIA, 'IQR Carro', 'IQR Moto']]

    grafico_comparativo = bsc.copy()
    grafico_comparativo['Atingimento Total'] = grafico_comparativo.sum(axis=1)
    
    bsc_comparativo = bsc.pivot_table(columns=[ROUTING_CODE,MES], aggfunc='median')
    bsc_comparativo.fillna("", inplace=True)

    bsc['KPI'] = bsc[MES]
    bsc_geral = bsc.pivot_table(columns='KPI', aggfunc='median')
    bsc_geral.fillna(0, inplace=True)

    pesos_pivotado = pesos.pivot_table(columns=MES, aggfunc='median')
    bsc_geral['Peso'] = bsc_geral.index.map(pesos_pivotado.iloc[:, 0]) * 100
    bsc_comparativo['Peso'] = bsc_comparativo.index.map(pesos_pivotado.iloc[:, 0]) * 100

    totals = bsc_geral.sum()
    bsc_geral.loc['Atingimento Total'] = totals
    bsc_geral = bsc_geral.applymap(lambda x: f'{x:.0f}%' if isinstance(x, (int, float)) and not np.isnan(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (float, int)) and not np.isnan(x) else x)

    bsc_comparativo.iloc[:, :-1] = bsc_comparativo.iloc[:, :-1].applymap(lambda x: f'{x:.0f}%' if isinstance(x, (int, float)) and not np.isnan(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (float, int)) and not np.isnan(x) else x)
    bsc_comparativo['Peso'] = bsc_comparativo['Peso'].apply(lambda x: f'{x:.0f}' if np.isfinite(x) and x == int(x) else f'{x:.2f}' if np.isfinite(x) else '')

    def reorder_dataframe(df, order):
        new_order = [item for item in order if item in df.index]
        df = df.reindex(new_order)
        return df

    order = [ABS, PART_TREN_LOGGERS, PART_TREN_LIDERES, APROV_TREN_LOGGERS, APROV_TREN_LIDERES, 'Programa 5S  [XD]', CUMPR_ROT_QUALIDADE, CONFORMIDADE, SLA, OPAV, ATING_AUDITORIA, 'Atingimento Total']

    bsc_geral = reorder_dataframe(bsc_geral, order)
    bsc_comparativo = reorder_dataframe(bsc_comparativo, order)
    resultados_geral = reorder_dataframe(resultados_geral, order)
    resultados_comparativo = reorder_dataframe(resultados_comparativo, order)

    bsc_geral_styled = bsc_geral.style.apply(PesoAtingimento.color_achievement, type='Peso', axis=1)
    bsc_comparativo_styled = bsc_comparativo.style.apply(PesoAtingimento.color_achievement, type='Peso', axis=1)

    metas_pivotado = metas.pivot_table(columns=MES, aggfunc='median')
    resultados_geral['Meta'] = resultados_geral.index.map(metas_pivotado.iloc[:, 0])

    resultados_geral.fillna("", inplace=True)
    resultados_geral = resultados_geral.applymap(lambda x: x * 100 if isinstance(x, (int, float)) else x)
    resultados_geral = resultados_geral.applymap(lambda x: f'{x:.0f}%' if isinstance(x, (int, float)) and not np.isnan(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (float, int)) and not np.isnan(x) else x)

    resultados_comparativo.fillna("", inplace=True)
    resultados_comparativo = resultados_comparativo.applymap(lambda x: x * 100 if isinstance(x, (int, float)) else x)
    resultados_comparativo = resultados_comparativo.applymap(lambda x: f'{x:.0f}%' if isinstance(x, (int, float)) and not np.isnan(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (float, int)) and not np.isnan(x) else x)

    metas = metas.applymap(lambda x: x * 100 if isinstance(x, (int, float)) else x)
    resultados = resultados.applymap(lambda x: x * 100 if isinstance(x, (int, float)) else x)
    resultados['Mês'] = resultados[MES]
    resultados.set_index('Mês', inplace=True)

    return resultados, resultados_geral, resultados_comparativo, bsc_geral_styled, bsc_comparativo_styled, metas, grafico_comparativo



