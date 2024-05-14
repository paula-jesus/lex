import pandas as pd
from utils import GerarTabelas, FormatoNumeros, PesoAtingimento
from consts import *
from estilizador import Dataframes
from functools import reduce
import streamlit as st

last_month = pd.to_datetime('today') - pd.DateOffset(months=1)
tabela = GerarTabelas()

def process_data(type, type_abrev, key=None):
    filenames = ["opav", "produtividade", "inventario", "abs", "two_hrs", "sla", "loss"]
    dfs = [tabela.gerar_dados(filename) for filename in filenames]
    dados_looker = reduce(lambda left,right: pd.merge(left,right,on=['routing_code', 'month'], how='outer', validate="many_to_many"), dfs)

    sheet_names = ['fonte_oficial', 'peso_kpis', 'fonte_metas']
    dados_planilha, dados_pesos, dados_metas_planilha = [GerarTabelas.gerar_tabela_sheets(name) for name in sheet_names]

    dados_looker = Dataframes.preprocess(dados_looker, 'type_dc', type)
    dados_planilha = Dataframes.preprocess(dados_planilha, 'BASE', type_abrev)
    dados_metas_planilha = Dataframes.preprocess(dados_metas_planilha, 'BASE', type_abrev)
    dados_pesos = Dataframes.preprocess(dados_pesos, 'BASE', type_abrev)

    if type_abrev == 'XD':
        columns_planilha = [AUDITORIA, AUTOAVALIACAO, PROGRAMA5S, ADERENCIA, CUSTO_OLD]

    if type_abrev == 'Ag':
        columns_planilha = [AUDITORIA, AUTOAVALIACAO, ADERENCIA, CUSTO_OLD]
        
    columns_metas_pesos = [AUDITORIA, AUTOAVALIACAO, OPAV, PROGRAMA5S_PERCENT, PRODUTIVIDADE, LOSS, ABSENTEISMO_PERCENT, ADERENCIA, INVENTARIO_AG, CUSTOAG, INVENTARIO_XD, CUSTOXD, HE, INTER, SLA_PERCENT]

    dados_planilha = FormatoNumeros.convert_to_numeric(dados_planilha, columns_planilha)
    dados_metas_planilha = FormatoNumeros.convert_to_numeric(dados_metas_planilha, columns_metas_pesos)
    dados_pesos = FormatoNumeros.convert_to_numeric(dados_pesos, columns_metas_pesos)

    dados_compilados = pd.merge(dados_looker, dados_planilha, on=['month', 'routing_code'], how='inner', validate="many_to_many")

    dados_compilados['month'] = dados_compilados['month'].dt.to_timestamp().dt.strftime('%Y-%m')

    dados_compilados[['sla', 'opav', 'abs', AUDITORIA,AUTOAVALIACAO, ADERENCIA]] = dados_compilados[['sla', 'opav', 'abs', AUDITORIA,AUTOAVALIACAO, ADERENCIA]] * 100
    dados_compilados[[PROGRAMA5S]] = dados_compilados[[PROGRAMA5S]] * 10
    dados_metas_planilha[[ OPAV, ABSENTEISMO_PERCENT, ADERENCIA, HE, INTER, AUDITORIA,AUTOAVALIACAO]] = dados_metas_planilha[[ OPAV, ABSENTEISMO_PERCENT, ADERENCIA, HE, INTER, AUDITORIA,AUTOAVALIACAO]] * 100
    dados_metas_planilha[[PROGRAMA5S_PERCENT]] = dados_metas_planilha[[PROGRAMA5S_PERCENT]] * 100
    dados_pesos[[ OPAV, ABSENTEISMO_PERCENT, ADERENCIA, INVENTARIO_AG, CUSTOAG, INVENTARIO_XD, CUSTOXD, HE, INTER, AUDITORIA,AUTOAVALIACAO, PRODUTIVIDADE, SLA_PERCENT, LOSS, PROGRAMA5S_PERCENT]] = dados_pesos[[ OPAV, ABSENTEISMO_PERCENT, ADERENCIA, INVENTARIO_AG, CUSTOAG, INVENTARIO_XD, CUSTOXD, HE, INTER, AUDITORIA,AUTOAVALIACAO, PRODUTIVIDADE, SLA_PERCENT, LOSS, PROGRAMA5S_PERCENT]] * 100

    if key == 'xxds' or key == 'xag':
        selected_values = st.sidebar.multiselect("Routing Code", dados_compilados['routing_code'].unique(), key=key)
        if selected_values:
            dados_compilados = dados_compilados[dados_compilados['routing_code'].isin(selected_values)]
            dados_metas_planilha = dados_metas_planilha[dados_metas_planilha['routing_code'].isin(selected_values)]

    if key == 'comparar_bases_ag' or key == 'comparar_bases_xd':
        routing_code = st.multiselect('Routing Code', dados_compilados['routing_code'].unique(), placeholder='Selecione um ou mais routing codes', key=key)
        if routing_code:
            dados_compilados = dados_compilados[dados_compilados['routing_code'].isin(routing_code)]
            dados_metas_planilha = dados_metas_planilha[dados_metas_planilha['routing_code'].isin(routing_code)]
            dados_pesos = dados_pesos[dados_pesos['routing_code'].isin(routing_code)]

    if type_abrev == 'XD':
        dados_compilados = dados_compilados.drop(['sla'], axis=1, errors='ignore')

    dados_compilados.rename(columns={'month': 'Mês', 'opav': OPAV, 'produtividade_media': PRODMEDIA, 'loss_rate': LR,'Auto avaliacao':AUTOAVALIACAO,'sla':SLA,'backlog':'Backlog','two_hrs':O2HE,'abs':ABS,'cnt_interjornada':O11INTER, 'percent_inventoried': INVENTARIO, ADERENCIA: TREINAMENTO, CUSTO_OLD: CUSTO}, inplace=True)

    if type_abrev == 'Ag':
        dados_metas_planilha.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, SLA_PERCENT: SLA, INVENTARIO_AG: INVENTARIO, LOSS: LR, CUSTOAG: CUSTO, ADERENCIA: TREINAMENTO}, inplace=True)
        dados_pesos.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, SLA_PERCENT: SLA, INVENTARIO_AG: INVENTARIO, LOSS: LR, CUSTOAG: CUSTO, ADERENCIA: TREINAMENTO}, inplace=True)

    if type_abrev == 'XD':    
        dados_metas_planilha.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, PROGRAMA5S_PERCENT: PROGRAMA5S, INVENTARIO_XD: INVENTARIO, LOSS: LR, CUSTOXD: CUSTO, ADERENCIA: TREINAMENTO}, inplace=True)
        dados_pesos.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, PROGRAMA5S_PERCENT: PROGRAMA5S, INVENTARIO_XD: INVENTARIO, LOSS: LR, CUSTOXD: CUSTO, ADERENCIA: TREINAMENTO}, inplace=True)

    dados_metas_planilha_pivot = dados_metas_planilha.copy()

    dados_lex_gauge = dados_compilados[dados_compilados['Mês'] == last_month.strftime('%Y-%m')]
    tabela_pivot = dados_compilados.pivot_table(columns='Mês', aggfunc='median')
    comparativo = dados_compilados.pivot_table(columns='routing_code', aggfunc='median')
    comparativo = comparativo.reset_index()
    tabela_pivot = tabela_pivot.reset_index()

    metas_pivot = Dataframes.ajustar_pivotar(dados_metas_planilha, key=key)
    pesos_pivot = Dataframes.ajustar_pivotar(dados_pesos, key=key)

    dados_metas_planilha_pivot = dados_metas_planilha_pivot.pivot_table(columns='routing_code', aggfunc='median')
    dados_metas_planilha_pivot = dados_metas_planilha_pivot.reset_index()
        
    metas_pivot = metas_pivot.reset_index()
    pesos_pivot = pesos_pivot.reset_index()

    dados_metas_pesos = pd.merge(dados_metas_planilha_pivot, pesos_pivot, left_on='index', right_on='index', how='left', validate="one_to_one")
    dados_metas_pesos = Dataframes.rename_and_move_to_end(dados_metas_pesos, pesos_pivot, 'Peso')

    combined_df = pd.merge(tabela_pivot, metas_pivot, left_on='index', right_on='index', how='left', validate="one_to_one")
    dados_mergeados_meta = Dataframes.rename_and_move_to_end(combined_df, metas_pivot, 'Meta')
    tabela_com_pesos = pd.merge(dados_mergeados_meta, pesos_pivot, left_on='index', right_on='index', how='left', validate="one_to_one")
    dados_mergeados_meta = Dataframes.rename_and_move_to_end(tabela_com_pesos, pesos_pivot, 'Peso')
    dados_mergeados_meta.set_index(dados_mergeados_meta.columns[0], inplace=True)
    dados_mergeados_meta.index.name = None
    dados_mergeados_meta = dados_mergeados_meta.fillna('')

    comparativo_pesos = pd.merge(comparativo, metas_pivot, left_on='index', right_on='index', how='left', validate="one_to_one")
    comparativo_pesos = Dataframes.rename_and_move_to_end(comparativo_pesos, metas_pivot, 'Meta')
    comparativo_pesos = pd.merge(comparativo_pesos, pesos_pivot, left_on='index', right_on='index', how='left', validate="one_to_one")
    comparativo_pesos = Dataframes.rename_and_move_to_end(comparativo_pesos, pesos_pivot, 'Peso')
    comparativo_pesos.set_index(comparativo_pesos.columns[0], inplace=True)
    comparativo_pesos.index.name = None
    comparativo_pesos = comparativo_pesos.fillna('')

    detalhamento_comparativo = comparativo_pesos.copy()

    pivot_table_reset = dados_mergeados_meta.copy()

    if type_abrev == 'XD':
        row_labels_percent = [OPAV, ABS,AUDITORIA,AUTOAVALIACAO, INVENTARIO, TREINAMENTO, PROGRAMA5S]
        row_labels = [PROGRAMA5S,O2HE,O11INTER,PRODMEDIA]

    if type_abrev == 'Ag':
        row_labels_percent = [OPAV, ABS,AUDITORIA,AUTOAVALIACAO, INVENTARIO, TREINAMENTO, SLA]
        row_labels = [O2HE,O11INTER,PRODMEDIA]

    row_labels_finance = [LR, CUSTO]
    row_names = [O2HE,O11INTER,ABS,CUSTO,LR,OPAV]

    pivot_table_reset = FormatoNumeros.format_rows(pivot_table_reset, row_labels_percent, FormatoNumeros.format_func_percent)
    pivot_table_reset = FormatoNumeros.format_rows(pivot_table_reset, row_labels, FormatoNumeros.format_func)
    pivot_table_reset = FormatoNumeros.format_rows(pivot_table_reset, row_labels_finance, FormatoNumeros.format_func_finance)
    detalhamento_comparativo = FormatoNumeros.format_rows(detalhamento_comparativo, row_labels_percent, FormatoNumeros.format_func_percent)
    detalhamento_comparativo = FormatoNumeros.format_rows(detalhamento_comparativo, row_labels, FormatoNumeros.format_func)
    detalhamento_comparativo = FormatoNumeros.format_rows(detalhamento_comparativo, row_labels_finance, FormatoNumeros.format_func_finance)

    pivot_table_reset = pivot_table_reset.drop(columns='Peso')

    if type_abrev == 'XD':
        order = [ABS, O2HE, O11INTER, TREINAMENTO, PROGRAMA5S, OPAV, INVENTARIO, PRODMEDIA, LR, CUSTO, AUTOAVALIACAO, AUDITORIA, 'Atingimento'] 
    if type_abrev == 'Ag':
        order = [ABS, O2HE, O11INTER, TREINAMENTO, OPAV, INVENTARIO, PRODMEDIA, SLA, LR, CUSTO, AUTOAVALIACAO, AUDITORIA]

    pivot_table_reset = pivot_table_reset.reindex(order)
    dados_mergeados_meta = dados_mergeados_meta.reindex(order)
    comparativo_pesos = comparativo_pesos.reindex(order)

    comparativo_pesos = PesoAtingimento.process(comparativo_pesos, row_names)

    tabela_com_pesos_styled = PesoAtingimento.process(dados_mergeados_meta, row_names)

    tabela_com_pesos_styled = tabela_com_pesos_styled.style.apply(PesoAtingimento.color_achievement, type='Peso', axis=1)

    return tabela_com_pesos_styled, pivot_table_reset, dados_compilados, dados_metas_planilha, dados_lex_gauge, dados_metas_pesos, comparativo_pesos, detalhamento_comparativo, dados_pesos, pesos_pivot
