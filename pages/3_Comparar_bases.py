import streamlit as st
from estilizador import Page_config, Dataframes
import time
from consts import *
from resultados_h2 import create_tables
import plotly.express as px

estilizador = Page_config()
estilizador.set_page_config()

text = "Dados carregando... Duração entre 1 e 5 minutos ⌛"
loading_message = st.empty()
loading_message.progress(0, text=text)

st.info("Esse link será desativado em breve. Acesse o novo [link oficial](https://lex.data.loggi.com/) (você precisará logar na sua conta Loggi para acessar).")

loading_message.progress(30, text=text)

tab1, tab2 = st.tabs(["Agências","XDs"])

with tab1:
    
    _, _, resultados_comparativo, _, bsc_comparativo_styled, _, grafico = create_tables('Ag', 'comparativo', 'ag_comp')

    bsc_comparativo_styled = Dataframes.generate_html(bsc_comparativo_styled)
    resultados_comparativo = Dataframes.generate_html(resultados_comparativo)
    st.subheader('Atingimeto com pesos')
    st.write(bsc_comparativo_styled, unsafe_allow_html=True)
    st.divider()
    st.subheader('Detalhamento do resultado')
    st.write(resultados_comparativo, unsafe_allow_html=True)

    comparativo_pesos_transformado = grafico.sort_values(by='Atingimento Total', ascending=False)
    fig = px.line(comparativo_pesos_transformado, x=ROUTING_CODE, y='Atingimento Total', title='Atingimento Total', labels={'index': ROUTING_CODE, 'Atingimento Total': 'Atingimento Total'}, range_y=[0,100])
    fig.update_traces(mode='markers+lines', text=comparativo_pesos_transformado['Atingimento Total'], textposition='top center')
    st.plotly_chart(fig)


with tab2:

    _, _, resultados_comparativo, _, bsc_comparativo_styled, _, grafico = create_tables('XD', 'comparativo', 'xd_comp')

    bsc_comparativo_styled = Dataframes.generate_html(bsc_comparativo_styled)
    resultados_comparativo = Dataframes.generate_html(resultados_comparativo)
    st.subheader('Atingimeto com pesos')
    st.write(bsc_comparativo_styled, unsafe_allow_html=True)
    st.divider()
    st.subheader('Detalhamento do resultado')
    st.write(resultados_comparativo, unsafe_allow_html=True)

    comparativo_pesos_transformado = grafico.sort_values(by='Atingimento Total', ascending=False)
    fig = px.line(comparativo_pesos_transformado, x=ROUTING_CODE, y='Atingimento Total', title='Atingimento Total', labels={'index': ROUTING_CODE, 'Atingimento Total': 'Atingimento Total'}, range_y=[0,100])
    fig.update_traces(mode='markers+lines')
    st.plotly_chart(fig)

loading_message.progress(100, text=text)
time.sleep(1)
loading_message.empty()
