import pandas as pd
from utils import GerarTabelas
from consts import *
import numpy as np
from functools import reduce

class Ajustes_tabelas:
    def convert_month(dfs):
        for df in dfs:
            df['month'] = pd.to_datetime(df['month']).dt.to_period('M')
        return dfs

    def change_na(dfs):
        for df in dfs:
            df.replace("N/A", "", inplace=True)
        return dfs

    def config_columns_numeric(dfs):
        cols_to_exclude = ['BASE', 'type_dc', 'routing_code', 'month']
        for df in dfs:
            cols_to_convert = [col for col in df.columns if col not in cols_to_exclude]
            df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors='coerce')

    def rename_columns_before_merge(df, suffix, exclude_cols=[]):
        df_copy = df.copy()
        df_copy.columns = [f"{col} {suffix}" if col not in exclude_cols else col for col in df_copy.columns]
        return df_copy
    
    def reorder_dataframe(df, order):
        new_order = [item for item in order if item in df.index]
        df = df.reindex(new_order)
        return df
    
    
class Gerar_mergear_tabelas:
    
    def gerar_tabelas(self, semestre=None):
        tabela = GerarTabelas()
        if semestre == 'H1':
            filenames = ["opav", "produtividade", "inventario", "abs", "two_hrs", "sla", "loss"]
            sheet_names = ['fonte_oficial', 'peso_kpis', 'fonte_metas']
        else:
            filenames = ["opav", "abs", "sla", "iqr"]
            sheet_names = ['fonte_oficial_h2', 'peso_kpis_h2_2024', 'fonte_metas_h2_2024']
        dfs = [tabela.gerar_dados(filename) for filename in filenames]
        dados_looker = reduce(lambda left,right: pd.merge(left,right,on=['routing_code', 'month'], how='outer', validate="many_to_many"), dfs)
        dados_planilha, pesos, metas = [GerarTabelas.gerar_tabela_sheets(name) for name in sheet_names]

        return dados_looker, dados_planilha, pesos, metas

    def dfs_mergeados(type, semestre=None):
        gerar_tabelas = Gerar_mergear_tabelas()
        dados_looker, dados_planilha, pesos, metas = gerar_tabelas.gerar_tabelas(semestre)
        dados_looker['routing_code'] = dados_looker['routing_code'].replace('CJ2', 'XDCJ2')
        if semestre == None:
            dados_looker = dados_looker.rename(columns={'sla': 'SLA', 'abs': '% Absenteísmo', 'opav': 'OPAV', 'iqr_carro': 'IQR Carro', 'iqr_moto': 'IQR Moto'})
        dados_planilha = dados_planilha.drop('#', axis=1)
        Ajustes_tabelas.convert_month([dados_looker, dados_planilha, pesos, metas])
        Ajustes_tabelas.change_na([dados_looker, dados_planilha, pesos, metas])
        Ajustes_tabelas.config_columns_numeric([dados_looker, dados_planilha, pesos, metas])

        dados_planilha = dados_planilha[dados_planilha['BASE'] == type]
        metas = metas[metas['BASE'] == type]
        pesos = pesos[pesos['BASE'] == type]

        if type == 'XD' and semestre == None:
            dados_looker = dados_looker[['routing_code', 'month', 'SLA', '% Absenteísmo', 'OPAV']]
        if type == 'Ag' and semestre == None:
            dados_planilha = dados_planilha[['routing_code', 'month', '% Participação em Treinamentos [Loggers]', '% Participação em Treinamentos [Líderes]', '% Aprovação em Treinamentos [Loggers]', '% Aprovação em Treinamentos [Líderes]', '% Cumprimento das Rotinas da Qualidade', '% Atingimento da Auditoria Oficial']]

        resultados = pd.merge(dados_planilha, dados_looker, on=['routing_code', 'month'], how='left')
        resultados.rename(columns={'month': 'Mês', 'routing_code': 'Routing Code'}, inplace=True)
        metas.rename(columns={'month': 'Mês', 'routing_code': 'Routing Code'}, inplace=True)
        pesos.rename(columns={'month': 'Mês', 'routing_code': 'Routing Code'}, inplace=True)
        resultados.columns = resultados.columns.str.replace('% ', '')
        metas.columns = metas.columns.str.replace('% ', '')
        pesos.columns = pesos.columns.str.replace('% ', '')

        return resultados, pesos, metas
    
class CalcularPesos:    

    def calculate_columns(resultados_com_peso_meta, columns):
        for column in columns:
            resultados_com_peso_meta[f'{column} peso'] = resultados_com_peso_meta[f'{column} peso'].astype(float) * 100
            resultados_com_peso_meta[f'{column} resultado'] = resultados_com_peso_meta[f'{column} resultado'].astype(float)
            resultados_com_peso_meta[f'{column} meta'] = resultados_com_peso_meta[f'{column} meta'].astype(float)
            resultados_com_peso_meta[f'{column}'] = np.minimum(resultados_com_peso_meta[f'{column} peso'], (resultados_com_peso_meta[f'{column} resultado'] / resultados_com_peso_meta[f'{column} meta']) * resultados_com_peso_meta[f'{column} peso'])

    def calculate_columns_baixo_melhor(resultados_com_peso_meta, columns):
        for column in columns:
            resultados_com_peso_meta[f'{column} peso'] = resultados_com_peso_meta[f'{column} peso'].astype(float) * 100
            resultados_com_peso_meta[f'{column} resultado'] = resultados_com_peso_meta[f'{column} resultado'].astype(float)
            resultados_com_peso_meta[f'{column} meta'] = resultados_com_peso_meta[f'{column} meta'].astype(float)
            condition = (resultados_com_peso_meta[f'{column} resultado'] > resultados_com_peso_meta[f'{column} meta']) & (resultados_com_peso_meta[f'{column} resultado'].notna()) & (resultados_com_peso_meta[f'{column} meta'].notna())
            resultados_com_peso_meta.loc[condition, f'{column}'] = 0
            resultados_com_peso_meta.loc[~condition & resultados_com_peso_meta[f'{column} resultado'].notna() & resultados_com_peso_meta[f'{column} meta'].notna(), f'{column}'] = resultados_com_peso_meta[f'{column} peso']