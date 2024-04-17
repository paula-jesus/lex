import streamlit as st
import pandas as pd 
from io import BytesIO


class PageStyler:
    def __init__(self):
        pass

    def apply_general_css(self):
        """
        Function to apply general CSS styling for the Streamlit app.

        No arguments or return value.
        """
        st.markdown(
            """
        <style>

        /* Fonte dos subtítulos */
        h2 {
        font-family: Monteserrat, sans-serif;
        }

        /* Fonte do texto personalizado do sidebar */
        p {
        font-family: Monteserrat, sans-serif;
        }

        /* Texto padrão */
        .custom-text {
        font-family: Monteserrat, sans-serif;
        text-align: justify; /* Justifica o texto */
        }

        /* Largura máxima da área de escrita */
        .css-1y4p8pa {
        max-width: 975px; 
        }

        /* Largura máxima da área de escrita */
        .st-emotion-cache-1y4p8pa {
        max-width: 62rem; 
        }

        /* Formatação do título */
        h1 {
        text-align: center; 
        font-size: 30px; 
        font-family: Monteserrat, sans-serif; 
        font-weight: 400;
        }

        /* Créditos e documentação */
        .custom-sidebar-footer {
        position: relative;
        bottom: 0px; 
        left: 0;
        width: 100%;
        font-size: 14px;
        text-align: left;
        }

        /* Estilos para links quando o mouse passa sobre eles */
        .custom-sidebar-footer a:hover {
        text-decoration: underline;
        }

        /* Estilos para links visitados */
        .custom-sidebar-footer a:visited {
        }

        /* Formatação do subtítulo padrão */
        .subtitle {
        font-family: Monteserrat, sans-serif;
        font-size: 20px;
        font-weight: bold;
        }

        [data-testid=stSidebar] [data-testid=stImage]{
        text-align: center;
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 100%;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def apply_sidebar_css(self):
        """
        Function to apply custom CSS styling to the Streamlit sidebar.
        The styling includes a background image and positioning adjustments.

        No arguments or return value.
        """
        st.markdown(
            """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Imagem_Logo_Completo_Azul.png/250px-Imagem_Logo_Completo_Azul.png);
                background-repeat: no-repeat;
                padding-top: 40px;
                background-position: 20px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }
        </style>
        """,
            unsafe_allow_html=True,
        )    


class Dataframes:
    def generate_html(df):
        """
        Generates an HTML representation of the DataFrame.

        Args:
            df (DataFrame): The DataFrame to convert to HTML.

        Returns:
            str: The HTML representation of the DataFrame.
        """
        rendered_table = df.to_html()
        html = """
        <div style="display: flex; justify-content: center;">
        <div style="max-height: 500px; overflow-y: auto;">
                {}
        """.format(rendered_table)
        return html

    def ajustar_pivotar(df, key=None):
        """
        Filters the DataFrame for the last month and pivots it.

        Args:
            df (DataFrame): The DataFrame to filter and pivot.

        Returns:
            DataFrame: The filtered and pivoted DataFrame.
        """
        if key != 'comparar_bases':
            df = df[df['month'] == df['month'].max()]
        return df.pivot_table(columns='month', aggfunc='median')
    
    def rename_and_move_to_end(df, df2, new_column_name):
        """
        Renames the last column of df2 and moves it to the end of df.

        Args:
            df (DataFrame): The DataFrame to modify.
            df2 (DataFrame): The DataFrame whose last column to rename.
            new_column_name (str): The new name for the column.

        Returns:
            DataFrame: The modified DataFrame.
        """
        old_column_name = df2.columns[-1]
        df = df.rename(columns={old_column_name: new_column_name})
        columns = df.columns.tolist()
        columns.remove(new_column_name)
        columns.append(new_column_name)
        return df[columns]

    def preprocess(df, column, value):
        """
        Preprocesses the DataFrame based on several conditions.

        Args:
            df (DataFrame): The DataFrame to preprocess.
            column (str): The name of the column to filter.
            value (str): The value to filter the column by.

        Returns:
            DataFrame: The preprocessed DataFrame.
        """
        mask = df[column] == value
        df = df[mask]
        if '#' in df.columns:
            df = df.drop('#', axis=1)
        if 'month' in df.columns:
            df['month'] = pd.to_datetime(df['month']).dt.to_period('M')
        if 'routing_code' in df.columns:
            df['routing_code'] = df['routing_code'].replace('XDCJ2', 'CJ2')
        df = df.replace('N/A', '')
        return df

    def gerar_tabela_final(df1, df2):
        df1_html = Dataframes.generate_html(df1)
        df2_html = Dataframes.generate_html(df2)
        on = st.toggle('Visualizar detalhamento dos resultados')
        if on:
            st.write("  ")
            st.write("  ")
            st.write(df1_html, unsafe_allow_html=True)
            st.write("  ")
            st.download_button(
                label="Baixar tabela",
                data=df1.to_csv().encode('utf-8'),
                file_name='Resultados_BSC.csv',
                mime='csv',
            )
            st.divider()
            st.subheader('Detalhamento dos resultados')
            st.write(df2_html, unsafe_allow_html=True)
            st.write("  ")
            st.download_button(
                label="Baixar tabela",
                data=df2.to_csv().encode('utf-8'),
                file_name='Detalhamento_BSC.csv',
                mime='csv',
            )
            st.write("  ")
        else:
            st.write("  ")
            st.write("  ")
            st.write(df1_html, unsafe_allow_html=True)
            st.write("  ")
            st.download_button(
                label="Baixar tabela",
                data=df1.to_csv().encode('utf-8'),
                file_name='Detalhamento_BSC.csv',
                mime='csv',
            )
            st.write("  ")
