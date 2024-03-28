import streamlit as st
import pandas as pd
from consts import *
from trat_dataframes import process_data
from graficos import Charts

def trat_graficos(type_abrev):

    if type_abrev == 'Ag':
        type = 'Agência'
    elif type_abrev == 'XD':
        type = 'Crossdocking'
    
    centered_table, tabela_detalhamento, dados_compilados, dados_lex_gauge, dados_metas_planilha = process_data(type, type_abrev, key="trat")

    dados_compilados['Mês'] = pd.to_datetime(dados_compilados['Mês'])
    dados_compilados.set_index('Mês', inplace=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Pessoas","Qualidade","Entrega", "Financeiro", "Auditoria"])

    with tab1:

        col1, col2 = st.columns([1.1, 1])
        column_name = ADERENCIA
        dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, 'Aderência ao Plano de Capacitação da Qualidade', f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, 'Aderência ao Plano de Capacitação da Qualidade', meta_value_decimal, 'green', 'red', 0, 100, [90, 100], [0, 90]))

        col1, col2 = st.columns([1.1, 1])
        column_name = ABS
        dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, ABS, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, ABS, meta_value_decimal, 'red', 'green', 0, 10, [0, meta_value_decimal], [meta_value_decimal, 10]))

        col1, col2 = st.columns([1.1, 1])
        column_name = O2HE
        dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, O2HE, f"Meta: {meta_value_str}", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, O2HE, meta_value_decimal, 'red', 'green', 0, 100, [0, 0], [0, 100]))

        col1, col2 = st.columns([1.1, 1])
        column_name = O11INTER
        dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, O11INTER, f"Meta: {meta_value_str}", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, O11INTER, meta_value_decimal, 'red', 'green', 0, 100, [0, 0], [0, 100]))

    with tab2:

        col1, col2 = st.columns([1.1, 1])
        column_name  = OPAV
        dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, OPAV, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, OPAV, meta_value_decimal, 'red', 'green', 0, 100, [0, meta_value_decimal], [meta_value_decimal, 100]))

        if type_abrev == 'XD':
                col1, col2 = st.columns([1.1, 1])
                column_name = PROGRAMA5S
                dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
                meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
                col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, PROGRAMA5S, f"Meta: {meta_value_percent}%", meta_value_decimal*10, meta_value_decimal*10))
                col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, PROGRAMA5S, meta_value_decimal*10, 'green', 'red', 0, 100, [meta_value_decimal*10, 100], [0, meta_value_decimal*10]))

        col1, col2 = st.columns([1.1, 1])
        column_name = INVENTARIO
        dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, INVENTARIO, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, INVENTARIO, meta_value_decimal, 'green', 'red', 0, 100, [meta_value_decimal, 100], [0, meta_value_decimal]))

    with tab3:

        if type_abrev == 'Ag':    
            col1, col2 = st.columns([1.1, 1])
            column_name = SLA
            dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
            meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
            col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, 'SLA', f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
            col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, 'SLA', meta_value_decimal, 'green', 'red', 0, 100, [meta_value_decimal, 100], [0, meta_value_decimal]))

        col1, col2 = st.columns([1.1, 1])
        column_name = PRODMEDIA
        dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, PRODMEDIA, f"Meta: {meta_value_str}", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, PRODMEDIA, meta_value_decimal, 'green', 'red', 0, 1500, [meta_value_decimal, 1500], [0, meta_value_decimal]))

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
        col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, CUSTO, meta_value_decimal, 'red', 'green', 0, 10, [0, meta_value_decimal], [meta_value_decimal, 100]))

    with tab5:

        col1, col2 = st.columns([1.1, 1])
        column_name = AUDITORIA
        dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, AUDITORIA, f"Meta: {meta_value_str}", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, AUDITORIA, meta_value_decimal, 'green', 'red', 0, 100, [meta_value_decimal, 100], [0, meta_value_decimal]))

        col1, col2 = st.columns([1.1, 1])
        column_name = AUTOAVALIACAO
        dados_compilados_resampled, value = Charts.process_data(dados_compilados, column_name)
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(dados_metas_planilha, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_compilados_resampled, column_name, AUTOAVALIACAO, f"Meta: {meta_value_str}", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(dados_lex_gauge, column_name, AUTOAVALIACAO, meta_value_decimal, 'green', 'red', 0, 100, [meta_value_decimal, 100], [0, meta_value_decimal]))




