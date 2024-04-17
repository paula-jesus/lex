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
        columns_planilha = [AUDITORIA, AUTOAVALIACAO, PROGRAMA5S, ADERENCIA, CUSTO]

    if type_abrev == 'Ag':
        columns_planilha = [AUDITORIA, AUTOAVALIACAO, ADERENCIA, CUSTO]
        
    columns_metas_pesos = [AUDITORIA, AUTOAVALIACAO, OPAV, PROGRAMA5S_PERCENT, PRODUTIVIDADE, LOSS, ABSENTEISMO_PERCENT, ADERENCIA, INVENTARIO_AG, CUSTOAG, INVENTARIO_XD, CUSTOXD, HE, INTER, SLA_PERCENT]

    dados_planilha = FormatoNumeros.convert_to_numeric(dados_planilha, columns_planilha)
    dados_metas_planilha = FormatoNumeros.convert_to_numeric(dados_metas_planilha, columns_metas_pesos)
    dados_pesos = FormatoNumeros.convert_to_numeric(dados_pesos, columns_metas_pesos)

    dados_compilados = pd.merge(dados_looker, dados_planilha, on=['month', 'routing_code'], how='inner', validate="many_to_many")

    dados_compilados['month'] = dados_compilados['month'].dt.to_timestamp().dt.strftime('%Y-%m')

    dados_compilados[['sla', 'opav', 'abs', AUDITORIA,AUTOAVALIACAO, ADERENCIA]] = dados_compilados[['sla', 'opav', 'abs', AUDITORIA,AUTOAVALIACAO, ADERENCIA]] * 100
    dados_compilados[[PROGRAMA5S]] = dados_compilados[[PROGRAMA5S]] * 10
    dados_metas_planilha[[ OPAV, ABSENTEISMO_PERCENT, ADERENCIA, HE, INTER, AUDITORIA,AUTOAVALIACAO]] = dados_metas_planilha[[ OPAV, ABSENTEISMO_PERCENT, ADERENCIA, HE, INTER, AUDITORIA,AUTOAVALIACAO]] * 100
    dados_metas_planilha[[PROGRAMA5S_PERCENT]] = dados_metas_planilha[[PROGRAMA5S_PERCENT]] * 10
    dados_pesos[[ OPAV, ABSENTEISMO_PERCENT, ADERENCIA, INVENTARIO_AG, CUSTOAG, INVENTARIO_XD, CUSTOXD, HE, INTER, AUDITORIA,AUTOAVALIACAO, PRODUTIVIDADE, SLA_PERCENT, LOSS]] = dados_pesos[[ OPAV, ABSENTEISMO_PERCENT, ADERENCIA, INVENTARIO_AG, CUSTOAG, INVENTARIO_XD, CUSTOXD, HE, INTER, AUDITORIA,AUTOAVALIACAO, PRODUTIVIDADE, SLA_PERCENT, LOSS]] * 100
    dados_pesos[[PROGRAMA5S_PERCENT]] = dados_pesos[[PROGRAMA5S_PERCENT]] * 10

    if key is None:
        selected_values = st.sidebar.multiselect("Routing Code", dados_compilados['routing_code'].unique(), key=key)
        if selected_values:
            dados_compilados = dados_compilados[dados_compilados['routing_code'].isin(selected_values)]
            dados_metas_planilha = dados_metas_planilha[dados_metas_planilha['routing_code'].isin(selected_values)]

    if type_abrev == 'XD':
        dados_compilados = dados_compilados.drop(['sla'], axis=1, errors='ignore')

    dados_compilados.rename(columns={'month': 'Mês', 'opav': OPAV, 'produtividade_media': PRODMEDIA, 'loss_rate': LR,'Auto avaliacao':AUTOAVALIACAO,'sla':SLA,'backlog':'Backlog','two_hrs':O2HE,'abs':ABS,'cnt_interjornada':O11INTER, 'percent_inventoried': INVENTARIO }, inplace=True)

    if type_abrev == 'Ag':
        dados_metas_planilha.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, SLA_PERCENT: SLA, INVENTARIO_AG: INVENTARIO, LOSS: LR, CUSTOAG: CUSTO}, inplace=True)
        dados_pesos.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, SLA_PERCENT: SLA, INVENTARIO_AG: INVENTARIO, LOSS: LR, CUSTOAG: CUSTO}, inplace=True)

    if type_abrev == 'XD':    
        dados_metas_planilha.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, PROGRAMA5S_PERCENT: PROGRAMA5S, INVENTARIO_XD: INVENTARIO, LOSS: LR, CUSTOXD: CUSTO}, inplace=True)
        dados_pesos.rename(columns={ABSENTEISMO_PERCENT: ABS,HE: O2HE, INTER:O11INTER, PRODUTIVIDADE:PRODMEDIA, PROGRAMA5S_PERCENT: PROGRAMA5S, INVENTARIO_XD: INVENTARIO, LOSS: LR, CUSTOXD: CUSTO}, inplace=True)

    dados_lex_gauge = dados_compilados[dados_compilados['Mês'] == last_month.strftime('%Y-%m')]
    tabela_pivot = dados_compilados.pivot_table(columns='Mês', aggfunc='median')
    tabela_pivot = tabela_pivot.reset_index()

    metas_pivot = Dataframes.ajustar_pivotar(dados_metas_planilha)
    pesos_pivot = Dataframes.ajustar_pivotar(dados_pesos)
        
    metas_pivot = metas_pivot.reset_index()
    pesos_pivot = pesos_pivot.reset_index()

    combined_df = pd.merge(tabela_pivot, metas_pivot, left_on='index', right_on='index', how='left', validate="one_to_one")

    dados_mergeados_meta = Dataframes.rename_and_move_to_end(combined_df, metas_pivot, 'Meta')
    tabela_com_pesos = pd.merge(dados_mergeados_meta, pesos_pivot, left_on='index', right_on='index', how='left', validate="one_to_one")
    dados_mergeados_meta = Dataframes.rename_and_move_to_end(tabela_com_pesos, pesos_pivot, 'Peso')
    dados_mergeados_meta.set_index(dados_mergeados_meta.columns[0], inplace=True)
    dados_mergeados_meta.index.name = None
    dados_mergeados_meta = dados_mergeados_meta.fillna('')

    pivot_table_reset = dados_mergeados_meta.copy()

    if type_abrev == 'XD':
        row_labels_percent = [OPAV, ABS,AUDITORIA,AUTOAVALIACAO, INVENTARIO, ADERENCIA, PROGRAMA5S]
        row_labels = [PROGRAMA5S,O2HE,O11INTER,PRODMEDIA]

    if type_abrev == 'Ag':
        row_labels_percent = [OPAV, ABS,AUDITORIA,AUTOAVALIACAO, INVENTARIO, ADERENCIA, SLA]
        row_labels = [O2HE,O11INTER,PRODMEDIA]

    row_labels_finance = [CUSTO, LR]
    row_names = [O2HE,O11INTER,ABS,CUSTO,LR,OPAV]

    pivot_table_reset = FormatoNumeros.format_rows(pivot_table_reset, row_labels_percent, FormatoNumeros.format_func_percent)
    pivot_table_reset = FormatoNumeros.format_rows(pivot_table_reset, row_labels, FormatoNumeros.format_func)
    pivot_table_reset = FormatoNumeros.format_rows(pivot_table_reset, row_labels_finance, FormatoNumeros.format_func_finance)

    tabela_com_pesos_styled = PesoAtingimento.process(dados_mergeados_meta, row_names)

    centered_table = Dataframes.generate_html(tabela_com_pesos_styled)
    tabela_detalhamento = Dataframes.generate_html(pivot_table_reset)

    return centered_table, tabela_detalhamento, dados_compilados, dados_lex_gauge, dados_metas_planilha








