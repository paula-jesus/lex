import streamlit as st


class PageStyler:
    def __init__(self):
        pass

    def style_metric_cards(
        background_color: str = "#00000",
        border_size_px: int = 1,
        border_color: str = "#CCC",
        border_radius_px: int = 5,
        border_left_color: str = "#00bfff",
        box_shadow: bool = True,
    ):
        """
        Function to apply custom styling to metric cards.

        Args:
            background_color (str): Background color of the metric card.
            border_size_px (int): Border size in pixels.
            border_color (str): Border color of the metric card.
            border_radius_px (int): Border radius in pixels.
            border_left_color (str): Border left color of the metric card.
            box_shadow (bool): Whether to apply a box shadow.

        No return value.
        """
        box_shadow_str = (
            "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
            if box_shadow
            else "box-shadow: none !important;"
        )
        st.markdown(
            f"""
            <style>
                div[data-testid="metric-container"] {{
                    background-color: {background_color};
                    border: {border_size_px}px solid {border_color};
                    padding: 5% 5% 5% 10%;
                    border-radius: {border_radius_px}px;
                    border-left: 0.5rem solid {border_left_color} !important;
                    {box_shadow_str}
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )

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

class DataframeStyler:
    def __init__(_self):
        pass

    def write_styled_dataframe(df):
        """
        Function to display a styled DataFrame in the Streamlit app.

        Args:
            df (DataFrame): Input data table.

        No return value.
        """
        styled_df = df.style.hide_index()
        rendered_table = styled_df.to_html()
        centered_table = f"""
        <div style="display: flex; justify-content: center;">
        <div style="max-height: 500px; overflow-y: auto;">
                {rendered_table}
        """
        st.write(centered_table, unsafe_allow_html=True)

    def sample_dataframe(df, condition, sample_size):
        filtered_df = df[condition]
        return filtered_df.sample(n=min(sample_size, len(filtered_df)))