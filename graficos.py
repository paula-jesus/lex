import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class Charts:
    def process_data(df, column_name):
        """
        Processes the data and returns a resampled DataFrame and the median of a column.

        Args:
            df (DataFrame): The DataFrame to process.
            column_name (str): The name of the column to process.

        Returns:
            DataFrame, float: The resampled DataFrame and the median of the column.
        """
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
        value = df[column_name].median()
        df_resampled = df.resample('M')[column_name].median().reset_index()
        df_resampled['Mês'] = df_resampled['Mês'].dt.strftime('%b %Y')
        return df_resampled, value

    def get_meta_value(df, column_name):
        """
        Gets the median value of a column in the DataFrame in various formats.

        Args:
            df (DataFrame): The DataFrame to process.
            column_name (str): The name of the column to process.

        Returns:
            float, str, str: The median value as a decimal, as a percentage, and as a string.
        """
        df_meta = df[[column_name]].rename(columns={column_name: 'meta'})
        meta_value_decimal = df_meta['meta'].median()
        meta_value_percent = str(df_meta['meta'].median() * 100)
        meta_value_percent = meta_value_percent.rstrip('0').rstrip('.') if '.' in meta_value_percent else meta_value_percent
        meta_value_str = str(meta_value_decimal)
        meta_value_str = meta_value_str.rstrip('0').rstrip('.') if '.' in meta_value_str else meta_value_str
        return meta_value_decimal, meta_value_percent, meta_value_str
    
    def gauge_chart(df, column, title, meta_value_decimal, color_increasig, color_decreasing, range_x1, range_x2, intervalo_verde, intervalo_vermelho):
        """
        Creates a gauge chart.

        Args:
            df (DataFrame): The DataFrame to process.
            column (str): The name of the column to process.
            title (str): The title of the chart.
            meta_value_decimal (float): The reference value for the delta indicator.
            color_increasing (str): The color for increasing deltas.
            color_decreasing (str): The color for decreasing deltas.
            range_x1 (float): The minimum value for the gauge axis.
            range_x2 (float): The maximum value for the gauge axis.
            intervalo_verde (list): The range for the green step on the gauge.
            intervalo_vermelho (list): The range for the red step on the gauge.

        Returns:
            Figure: The created chart.
        """
        value = df[column].median()
        fig = go.Figure(
            go.Indicator(

                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': title, 'font': {'size': 18, 'color': 'black', 'family': 'Arial'}},
                delta={'reference': meta_value_decimal, 'increasing': {'color': color_increasig}, 'decreasing': {'color': color_decreasing}},
                number={'font': {'size': 21, 'color': 'black', 'family': 'Arial'}},
                gauge={
                    'axis': {'range': [range_x1, range_x2]},
                    'bar': {'color': '#8fe1ff'},
                    'steps': [
                        {'range': intervalo_vermelho, 'color': '#fab8a3'},  
                        {'range': intervalo_verde, 'color': '#c9f1ac'},  
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': value
                    }
                }
            ),
            layout={
                'annotations': [
                    {
                        'x': 0.5,
                        'y': -0.25,
                        'showarrow': False,
                        'text': "Valor referente ao último mês completo",
                        'xref': "paper",
                        'yref': "paper"
                    }
                ],
                'width': 500, 
                'height': 320
            }
        )
        return fig
    
    def create_area_plot(df, y_column, title, text, y0, y1):
        """
        Processes the data and returns a resampled DataFrame and the median of a column.

        Args:
            df (DataFrame): The DataFrame to process.
            column_name (str): The name of the column to process.

        Returns:
            DataFrame, float: The resampled DataFrame and the median of the column.
        """
        plot = px.area(df, x="Mês", y=y_column, title=title, height=330, width=500, color_discrete_sequence=['#00baff'])

        goal_line = go.layout.Shape(
            type="line",
            x0=df["Mês"].min(),
            x1=df["Mês"].max(),
            y0=y0,
            y1=y1,
            line=dict(
                color="#148bb8",
                width=2,
                dash="dashdot",
            ),
        )
        plot.add_annotation(
            x=df["Mês"].max(),
            y=y0,
            text=text,
            showarrow=False,
            font=dict(
                size=16,
                color="#148bb8"
            ),
            bgcolor="White",
            bordercolor="#148bb8",
            borderwidth=2,
            borderpad=4,
        )
        plot.update_layout(shapes=[goal_line], showlegend=False, yaxis_title=None)

        return plot
