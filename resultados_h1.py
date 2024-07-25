import streamlit as st
import pandas as pd
from utils import color_achievement, FormatoNumeros
from estilizador import Dataframes
from init_dataframes import Ajustes_tabelas, CalcularPesos, Gerar_mergear_tabelas
from consts import *
import streamlit as st
import numpy as np

def tabelas_resultados_h1(type, key=None):

    resultados, pesos, metas = Gerar_mergear_tabelas.dfs_mergeados(type, 'H1')

    resultados.fillna(0, inplace=True)

    resultados = resultados[resultados['Mês'] <= '2024-06']
    resultados = resultados[resultados['Mês'] >= '2024-01']
    pesos = pesos[pesos['Mês'] <= '2024-06']
    pesos = pesos[pesos['Mês'] >= '2024-01']

    if type == 'XD':
        resultados.drop(columns=['sla'], inplace=True)
    if type == 'Ag':
        resultados.drop(columns=[PROGRAMA5S], inplace=True)

    month = st.multiselect('Selecione o mês', resultados[MES].unique(), key=key)
    routing_code = st.multiselect('Selecione o routing code', resultados[ROUTING_CODE].unique())
    if month:
        resultados = resultados[resultados[MES].isin(month)]
    if routing_code:
        resultados = resultados[resultados[ROUTING_CODE].isin(routing_code)]

    resultados.rename(columns={'month': 'Mês', 'opav': OPAV, 'produtividade_media': PRODMEDIA, 'loss_rate': LR,'Auto avaliacao':AUTOAVALIACAO,'sla':SLA,'backlog':'Backlog','two_hrs':O2HE,'abs':ABS,'cnt_interjornada':O11INTER, 'percent_inventoried': INVENTARIO, ADERENCIA: TREINAMENTO, CUSTO_OLD: CUSTO}, inplace=True)
    if type == 'Ag':
            metas.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, SLA_PERCENT: SLA, INVENTARIO_AG: INVENTARIO, LOSS: LR, CUSTOAG: CUSTO, ADERENCIA: TREINAMENTO}, inplace=True)
            pesos.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, SLA_PERCENT: SLA, INVENTARIO_AG: INVENTARIO, LOSS: LR, CUSTOAG: CUSTO, ADERENCIA: TREINAMENTO}, inplace=True)
            order = [ABS, O2HE, O11INTER, TREINAMENTO, OPAV, INVENTARIO, PRODMEDIA, SLA, LR, CUSTO, AUTOAVALIACAO, AUDITORIA, 'Atingimento Total']
            columns_mais_melhor = [SLA, PRODMEDIA, INVENTARIO, TREINAMENTO, AUTOAVALIACAO, AUDITORIA]

    if type == 'XD':    
            metas.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, PROGRAMA5S_PERCENT: PROGRAMA5S, INVENTARIO_XD: INVENTARIO, LOSS: LR, CUSTOXD: CUSTO, ADERENCIA: TREINAMENTO}, inplace=True)
            pesos.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, PROGRAMA5S_PERCENT: PROGRAMA5S, INVENTARIO_XD: INVENTARIO, LOSS: LR, CUSTOXD: CUSTO, ADERENCIA: TREINAMENTO}, inplace=True)
            order = [ABS, O2HE, O11INTER, TREINAMENTO, PROGRAMA5S, OPAV, INVENTARIO, PRODMEDIA, LR, CUSTO, AUTOAVALIACAO, AUDITORIA, 'Atingimento Total'] 
            columns_mais_melhor =  [PRODMEDIA, PROGRAMA5S, INVENTARIO, TREINAMENTO, AUTOAVALIACAO, AUDITORIA]
            resultados[[PROGRAMA5S]] = resultados[[PROGRAMA5S]].applymap(lambda x: x * 10 if isinstance(x, (int, float)) else x)

    resultados['KPI'] = resultados[MES]
    resultados[[ABS, OPAV, AUDITORIA, AUTOAVALIACAO, TREINAMENTO]] = resultados[[ABS, OPAV, AUDITORIA, AUTOAVALIACAO, TREINAMENTO]].applymap(lambda x: x * 100 if isinstance(x, (int, float)) else x)
    resultados_comparativo = resultados.pivot_table(columns=[ROUTING_CODE,MES], aggfunc='median')

    pesos_nomeado = Ajustes_tabelas.rename_columns_before_merge(pesos, 'peso', [ROUTING_CODE, MES])
    metas_nomeado = Ajustes_tabelas.rename_columns_before_merge(metas, 'meta', [ROUTING_CODE, MES])
    resultados_nomeado = Ajustes_tabelas.rename_columns_before_merge(resultados, 'resultado', [ROUTING_CODE, MES])

    resultados_com_peso_meta = pd.merge(resultados_nomeado, metas_nomeado, on=[ROUTING_CODE, MES], how='left')
    resultados_com_peso_meta = pd.merge(resultados_com_peso_meta, pesos_nomeado, on=[ROUTING_CODE, MES], how='left')

    columns_menos_melhor = [ABS, OPAV, LR, CUSTO, O2HE, O11INTER]
    CalcularPesos.calculate_columns(resultados_com_peso_meta, columns_mais_melhor)
    CalcularPesos.calculate_columns_baixo_melhor(resultados_com_peso_meta, columns_menos_melhor)

    if type == 'XD':
        bsc = resultados_com_peso_meta[[ROUTING_CODE, MES, ABS, OPAV, PRODMEDIA, PROGRAMA5S, INVENTARIO, LR, CUSTO, TREINAMENTO, O2HE, O11INTER, AUTOAVALIACAO, AUDITORIA]]
    if type == 'Ag':
        bsc = resultados_com_peso_meta[[ROUTING_CODE, MES, SLA, ABS, OPAV, PRODMEDIA, INVENTARIO, LR, CUSTO, TREINAMENTO, O2HE, O11INTER, AUTOAVALIACAO, AUDITORIA]]

    grafico_comparativo = bsc.copy()
    grafico_comparativo['Atingimento Total'] = grafico_comparativo.sum(axis=1)

    bsc_comparativo = bsc.pivot_table(columns=[ROUTING_CODE,MES], aggfunc='median')
    bsc_comparativo.fillna("", inplace=True)

    pesos_pivotado = pesos.pivot_table(columns=MES, aggfunc='median')
    bsc_comparativo['Peso'] = bsc_comparativo.index.map(pesos_pivotado.iloc[:, 0]) * 100

    totals = bsc_comparativo.sum()
    bsc_comparativo.loc['Atingimento Total'] = totals
    bsc_comparativo.iloc[:, :-1] = bsc_comparativo.iloc[:, :-1].applymap(lambda x: f'{x:.0f}%' if isinstance(x, (int, float)) and not np.isnan(x) and x == int(x) else f'{x:.2f}%' if isinstance(x, (float, int)) and not np.isnan(x) else x)
    bsc_comparativo['Peso'] = bsc_comparativo['Peso'].apply(lambda x: f'{x:.0f}' if np.isfinite(x) and x == int(x) else f'{x:.2f}' if np.isfinite(x) else '')

    bsc_comparativo = Ajustes_tabelas.reorder_dataframe(bsc_comparativo, order)
    resultados_comparativo = Ajustes_tabelas.reorder_dataframe(resultados_comparativo, order)

    bsc_comparativo_styled = bsc_comparativo.style.apply(color_achievement, type='Peso', axis=1)

    resultados_comparativo.fillna("", inplace=True)
    if type == 'XD':
        row_labels_percent = [OPAV, ABS,AUDITORIA,AUTOAVALIACAO, INVENTARIO, TREINAMENTO, PROGRAMA5S]
        row_labels = [PROGRAMA5S,O2HE,O11INTER,PRODMEDIA]

    if type == 'Ag':
        row_labels_percent = [OPAV, ABS,AUDITORIA,AUTOAVALIACAO, INVENTARIO, TREINAMENTO, SLA]
        row_labels = [O2HE,O11INTER,PRODMEDIA]

    row_labels_finance = [LR, CUSTO]

    resultados_comparativo = FormatoNumeros.format_rows(resultados_comparativo, row_labels_percent, FormatoNumeros.format_func_percent)
    resultados_comparativo = FormatoNumeros.format_rows(resultados_comparativo, row_labels, FormatoNumeros.format_func)
    resultados_comparativo = FormatoNumeros.format_rows(resultados_comparativo, row_labels_finance, FormatoNumeros.format_func_finance)

    bsc_comparativo_styled = Dataframes.generate_html(bsc_comparativo_styled)
    resultados_comparativo = Dataframes.generate_html(resultados_comparativo)
    st.subheader('Atingimeto com pesos')
    st.write(bsc_comparativo_styled, unsafe_allow_html=True)
    st.divider()
    st.subheader('Detalhamento do resultado')
    st.write(resultados_comparativo, unsafe_allow_html=True)




