import streamlit as st
from consts import *
from graficos import Charts

def create_charts(metas, resultados, type):

    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Pessoas', 'Qualidade', 'Entrega', 'Financeiro', 'Auditoria'])

    with tab1:

        col1, col2 = st.columns([1.1, 1])
        column_name = ABS
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
        dados_area_chart, value = Charts.process_data(resultados, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, ABS, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(resultados, column_name, ABS, meta_value_decimal, 'red', 'green', 0, 10, [0, meta_value_decimal], [meta_value_decimal, 10]))

        column_name = PART_TREN_LOGGERS
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
        dados_area_chart, value = Charts.process_data(resultados, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, PART_TREN_LOGGERS, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(resultados, column_name, PART_TREN_LOGGERS, meta_value_decimal, 'green', 'red', 0, 100, [90, 100], [0, 90]))

        column_name = PART_TREN_LIDERES
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
        dados_area_chart, value = Charts.process_data(resultados, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, PART_TREN_LIDERES, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(resultados, column_name, PART_TREN_LIDERES, meta_value_decimal, 'green', 'red', 0, 100, [90, 100], [0, 90]))

        column_name = APROV_TREN_LOGGERS
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
        dados_area_chart, value = Charts.process_data(resultados, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, APROV_TREN_LOGGERS, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(resultados, column_name, APROV_TREN_LOGGERS, meta_value_decimal, 'green', 'red', 0, 100, [80, 100], [0, 80]))

        column_name = APROV_TREN_LIDERES
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
        dados_area_chart, value = Charts.process_data(resultados, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, APROV_TREN_LIDERES, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(resultados, column_name, APROV_TREN_LIDERES, meta_value_decimal, 'green', 'red', 0, 100, [80, 100], [0, 80]))

    with tab2:

        col1, col2 = st.columns([1.1, 1])
        column_name = CUMPR_ROT_QUALIDADE
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
        dados_area_chart, value = Charts.process_data(resultados, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, CUMPR_ROT_QUALIDADE, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(resultados, column_name, CUMPR_ROT_QUALIDADE, meta_value_decimal, 'green', 'red', 0, 100, [90, 100], [0, 90]))

        if type == 'XD':
            column_name = PROGRAMA5S
            meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
            dados_area_chart, value = Charts.process_data(resultados, column_name)
            col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, PROGRAMA5S, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
            col2.plotly_chart(Charts.gauge_chart(resultados, column_name, PROGRAMA5S, meta_value_decimal, 'green', 'red', 0, 100, [85, 100], [0, 85]))

            column_name = CONFORMIDADE
            meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
            dados_area_chart, value = Charts.process_data(resultados, column_name)
            col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, CONFORMIDADE, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
            col2.plotly_chart(Charts.gauge_chart(resultados, column_name, CONFORMIDADE, meta_value_decimal, 'green', 'red', 0, 100, [85, 100], [0, 85]))

    with tab3:

        col1, col2 = st.columns([1.1, 1])
        column_name = SLA
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
        dados_area_chart, value = Charts.process_data(resultados, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, SLA, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(resultados, column_name, SLA, meta_value_decimal, 'green', 'red', 0, 100, [97, 100], [0, 97]))

    with tab4:

        col1, col2 = st.columns([1.1, 1])
        column_name = OPAV
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
        dados_area_chart, value = Charts.process_data(resultados, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, OPAV, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(resultados, column_name, OPAV, meta_value_decimal, 'red', 'green', 0, 100, [0, 36], [0, 100]))

        if type == 'Ag':
            column_name = 'IQR Carro'
            meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
            dados_area_chart, value = Charts.process_data(resultados, column_name)
            col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, 'IQR Carro', f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
            col2.plotly_chart(Charts.gauge_chart(resultados, column_name, 'IQR Carro', meta_value_decimal, 'green', 'red', 0, 100, [100, 100], [0, 100]))

            column_name = 'IQR Moto'
            meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
            dados_area_chart, value = Charts.process_data(resultados, column_name)
            col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, 'IQR Moto', f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
            col2.plotly_chart(Charts.gauge_chart(resultados, column_name, 'IQR Moto', meta_value_decimal, 'green', 'red', 0, 100, [100, 100], [0, 100]))

    with tab5:

        col1, col2 = st.columns([1.1, 1])
        column_name = ATING_AUDITORIA
        meta_value_decimal, meta_value_percent, meta_value_str = Charts.get_meta_value(metas, column_name)
        dados_area_chart, value = Charts.process_data(resultados, column_name)
        col1.plotly_chart(Charts.create_area_plot(dados_area_chart, column_name, ATING_AUDITORIA, f"Meta: {meta_value_str}%", meta_value_decimal, meta_value_decimal))
        col2.plotly_chart(Charts.gauge_chart(resultados, column_name, ATING_AUDITORIA, meta_value_decimal, 'green', 'red', 0, 100, [100, 100], [0, 100]))