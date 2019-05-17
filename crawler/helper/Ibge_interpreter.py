import json

import numpy as np
import pandas as pd


class Interpreter:

    def __init__(self, json_data):
        self.df = pd.DataFrame.from_dict(json_data, orient='index')

    def count_occurrence(self, column, word):
        percent = self.df[column].str.contains(word).sum()
        na = self.df[column].isna().sum()
        return percent + na

    def count_numeric_interval(self, column, begin, end):
        percent = len(self.df[(self.df[column] >= begin) & (self.df[column] <= end)])
        na = self.df[column].isna().sum()
        return percent + na

    def remove_percent(self, column, column_type):
            # , to . for numeric transform
        self.df[column] = self.df[column].apply(
            lambda x: str(x).replace(',', '.'))

        # Remove %
        self.df[column] = self.df[column].apply(
            lambda x: str(x).replace(' %', ''))

        # Cast to float
        self.df[column].astype(column_type)

    def remove_word(self, column, word, column_type):
        # Remove matrículas
        self.df[column] = self.df[column].apply(
            lambda x: str(x).replace(word, ''))

        # Cast to int
        self.df[column].astype(column_type)


    def validate_gentilico(self):
        unique_values = len(pd.unique(self.df['Gentílico']))
        if unique_values <= 1:
            self.df.drop(['Gentílico'], axis=1, inplace=True)

    def validate_area_territorial(self):
        km = self.count_occurrence('Área da unidade territorial', 'km²')
        if km == len(self.df):
            # , to . for numeric transform
            self.df['Área da unidade territorial'] = \
                self.df['Área da unidade territorial'].apply(
                    lambda x: str(x).replace(',', '.'))

            # Remove km²
            self.df['Área da unidade territorial'] = \
                self.df['Área da unidade territorial'].apply(
                    lambda x: str(x).replace(' km²', ''))

            # Cast to float
            self.df['Área da unidade territorial'].astype('float64')
        else:
            raise Exception(
                'Coluna "Área da unidade territorial" fora do padrão')

    def validate_arborizacao(self):
        percent = self.count_occurrence('Arborização de vias públicas', '%')
        if percent == len(self.df):
            self.remove_percent('Arborização de vias públicas', 'float64')
        else:
            raise Exception(
                'Coluna "Arborização de vias públicas" fora do padrão')

    def validate_esgotamento(self):
        percent = self.count_occurrence('Esgotamento sanitário adequado', '%')
        if percent == len(self.df):
            self.remove_percent('Esgotamento sanitário adequado', 'float64')
        else:
            raise Exception(
                'Coluna "Esgotamento sanitário adequado" fora do padrão')

    def validate_urbanizacao_vias(self):
        percent = self.count_occurrence('Urbanização de vias públicas', '%')
        if percent == len(self.df):
            self.remove_percent('Urbanização de vias públicas', 'float64')
        else:
            raise Exception(
                'Coluna "Urbanização de vias públicas" fora do padrão')

    def validate_matriculas_fundamental(self):
        percent = self.count_occurrence(
            'Matrículas no ensino fundamental', 'matrículas')
        if percent == len(self.df):
            self.remove_word('Matrículas no ensino fundamental',
                             ' matrículas', 'int64')
        else:
            raise Exception(
                'Coluna "Matrículas no ensino fundamental" fora do padrão')

    def validate_matriculas_medio(self):
        percent = self.count_occurrence(
            'Matrículas no ensino médio', 'matrículas')
        if percent == len(self.df):
            self.remove_word('Matrículas no ensino médio',
                             ' matrículas', 'int64')
        else:
            raise Exception(
                'Coluna "Matrículas no ensino médio" fora do padrão')

    def validate_half_income(self):
        self.df.rename(
            columns={
                'Percentual da população com rendimento nominal mensal per capita de até 1/2 salário mínimo': 'Half income'
            }, inplace=True)

        percent = self.count_occurrence('Half income', '%')
        if percent == len(self.df):
            self.remove_percent('Half income', 'float64')
        else:
            raise Exception('Coluna "Half income" fora do padrão')

    def validate_ideb(self):
        self.df.rename(
            columns={
                'IDEB – Anos iniciais do ensino fundamental': 'IDEB'
            }, inplace=True)

        self.df.loc[self.df['IDEB'].str.contains('%', na=False), 'IDEB'] = np.nan
        self.df['IDEB'] = self.df['IDEB'].apply(lambda x: str(x).replace(',', '.'))
        self.df['IDEB'] = self.df['IDEB'].astype('float64')

        percent = self.count_numeric_interval('IDEB', 0, 10)
        if percent == len(self.df):
            pass
        else:
            raise Exception('Coluna "IDEB" fora do padrão')

    def interpret(self):
        self.validate_gentilico()
        self.validate_area_territorial()
        self.validate_arborizacao()
        self.validate_esgotamento()
        self.validate_urbanizacao_vias()
        self.validate_matriculas_fundamental()
        self.validate_matriculas_medio()
        self.validate_half_income()
        self.validate_ideb()


with open('./helper/downloaded_files/IBGE/ibge_cities_info.json') as f:
    data = json.load(f)

interpreter = Interpreter(data)
interpreter.interpret()
print(interpreter.df['IDEB'].head(10))
