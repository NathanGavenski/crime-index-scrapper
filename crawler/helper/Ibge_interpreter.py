import json

import numpy as np
import pandas as pd


class Interpreter:

    def __init__(self, json_data):
        self.df = pd.DataFrame.from_dict(json_data, orient='index')

    def show_out_standard_values(self, column, word):
        return self.df.loc[~self.df[column].str.contains(word, na=False), column]


    def count_occurrence(self, column, word, df=None):
        if df is None: df = self.df
        percent = df[column].str.contains(word, na=False).sum()
        na = df[column].isna().sum()
        return percent + na


    def count_numeric_interval(self, column, begin, end):
        percent = len(self.df[(self.df[column] >= begin) & (self.df[column] <= end)])
        na = self.df[column].isna().sum()
        return percent + na

    def remove_percent(self, column):
            # , to . for numeric transform
        self.df[column] = self.df[column].apply(
            lambda x: str(x).replace(',', '.'))

        # Remove %
        self.df[column] = self.df[column].apply(
            lambda x: str(x).replace(' %', ''))

        # Cast to float
        self.df[column] = pd.to_numeric(self.df[column], errors='coerce')

    def remove_word(self, column, word, replace_word='', remove_coma=False):
        # Remove matrículas
        self.df[column] = self.df[column].apply(
            lambda x: str(x).replace(word, replace_word))

        if remove_coma is True:
            self.df[column] = self.df[column].apply(lambda x: str(x).replace(',', '.'))

        # Cast to type
        self.df[column] = pd.to_numeric(self.df[column], errors='coerce')


    def validate_gentilico(self):
        unique_values = len(pd.unique(self.df['Gentílico']))
        if unique_values <= 1:
            self.df.drop(['Gentílico'], axis=1, inplace=True)

    def validate_area_territorial(self):
        km = self.count_occurrence('Área da unidade territorial', 'km²')
        if km == len(self.df):
            self.remove_word('Área da unidade territorial', 'km²', remove_coma=True)
        else:
            raise Exception(
                'Coluna "Área da unidade territorial" fora do padrão')

    def validate_arborizacao(self):
        percent = self.count_occurrence('Arborização de vias públicas', '%')
        if percent == len(self.df):
            self.remove_percent('Arborização de vias públicas')
        else:
            raise Exception(
                'Coluna "Arborização de vias públicas" fora do padrão')

    def validate_esgotamento(self):
        percent = self.count_occurrence('Esgotamento sanitário adequado', '%')
        if percent == len(self.df):
            self.remove_percent('Esgotamento sanitário adequado')
        else:
            raise Exception(
                'Coluna "Esgotamento sanitário adequado" fora do padrão')

    def validate_urbanizacao_vias(self):
        percent = self.count_occurrence('Urbanização de vias públicas', '%')
        if percent == len(self.df):
            self.remove_percent('Urbanização de vias públicas')
        else:
            raise Exception(
                'Coluna "Urbanização de vias públicas" fora do padrão')

    def validate_matriculas_fundamental(self):
        percent = self.count_occurrence(
            'Matrículas no ensino fundamental', 'matrículas')
        if percent == len(self.df):
            self.remove_word('Matrículas no ensino fundamental', ' matrículas')
        else:
            raise Exception(
                'Coluna "Matrículas no ensino fundamental" fora do padrão')

    def validate_matriculas_medio(self):
        percent = self.count_occurrence(
            'Matrículas no ensino médio', 'matrículas')
        if percent == len(self.df):
            self.remove_word('Matrículas no ensino médio', ' matrículas')
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
            self.remove_percent('Half income')
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

    def validate_school_minor(self):
        self.df.rename(
            columns={
                'Taxa de escolarização de 6 a 14 anos de idade': 'school_minor'
            }, inplace=True)

        percent = self.count_occurrence('school_minor', '%')
        if percent == len(self.df):
            self.remove_percent('school_minor')
        else:
            raise Exception('Coluna "school_minor" fora do padrão')

    def validate_estabelecimento_sus(self):
        self.df.rename(
            columns={
                'Estabelecimentos de Saúde SUS': 'estabelecimento_sus'
            }, inplace=True)

        percent = self.count_occurrence('estabelecimento_sus', 'estabelecimento')
        if percent == len(self.df):
            self.remove_word('estabelecimento_sus', 'estabelecimentos')
        else:
            out_standart = self.df.loc[~self.df['estabelecimento_sus'].str.contains('estabelecimento', na=False), 'estabelecimento_sus']
            out_standart = pd.DataFrame(out_standart)

            percent = out_standart['estabelecimento_sus'].str.contains('×1000', na=False).sum()

            if percent == len(out_standart):
                self.df.loc[self.df['estabelecimento_sus'].str.contains('×1000'), 'estabelecimento_sus'] = np.nan
                return self.validate_estabelecimento_sus()
            raise Exception('Coluna "Estabelecimentos de Saúde SUS" fora do padrão')

    def validate_IDHM(self):
        self.df.rename(
            columns={
                'Índice de Desenvolvimento Humano Municipal (IDHM)': 'IDHM'
            }, inplace=True)

        percent = self.count_occurrence('IDHM', ',')
        if percent == len(self.df):
            self.remove_word('IDHM', ',', '.')
        else:
            raise Exception('Coluna "IDHM" fora do padrão')
        

    def validate_infant_death(self):
        self.df.rename(
            columns={
                'Mortalidade Infantil': 'infant_death'
            }, inplace=True)

        percent = self.count_occurrence('infant_death','vivos')
        if percent == len(self.df):
            self.remove_word('infant_death', 'óbitos por mil nascidos vivos', remove_coma=True)
            pass
        else:
            out_standart = self.df.loc[~self.df['infant_death'].str.contains('vivos', na=False), 'infant_death']
            out_standart = pd.DataFrame(out_standart)

            percent = self.count_occurrence('infant_death', '-', out_standart)
            if percent == len(out_standart):
                self.df.loc[self.df['infant_death'].str.contains('-', na=False), 'infant_death'] = np.nan
                return self.validate_infant_death()
            raise Exception('Coluna "Mortalidade Infantil", fora do padrão')

    def validate_diarrhea_hospitalizations(self):
        self.df.rename(
            columns={
                'Internações por diarreia': 'diarrhea_hospitalizations'
            }, inplace=True)

        percent = self.count_occurrence('diarrhea_hospitalizations', 'internações por mil habitantes')
        if percent == len(self.df):
            self.remove_word('diarrhea_hospitalizations', 'internações por mil habitantes', remove_coma=True)
        else:
            raise Exception('Coluna "Internações por diarreia" fora do padrão')

    def validate_fundamental_teachers(self):
        self.df.rename(
            columns={
                'Docentes no ensino fundamental': 'fundamental_teachers'
            }, inplace=True)

        percent = self.count_occurrence('fundamental_teachers', 'docentes')
        if percent == len(self.df):
            self.remove_word('fundamental_teachers', 'docentes')
        else:
            raise Exception('Coluna "Docentes no ensino fundamental" fora do padrão')

    def validate_medium_teachers(self):
        self.df.rename(
            columns={
                'Docentes no ensino médio': 'medium_teachers'
            }, inplace=True)

        percent = self.count_occurrence('medium_teachers', 'docentes')
        if percent == len(self.df):
            self.remove_word('medium_teachers', 'docentes')
        else:
            raise Exception('Coluna "Docentes no ensino médio" fora do padrão')

    def validate_fundamental_schools(self):
        self.df.rename(
            columns={
                'Número de estabelecimentos de ensino fundamental': 'fundamental_schools'
            }, inplace=True)

        percent = self.count_occurrence('fundamental_schools', 'escolas')
        if percent == len(self.df):
            self.remove_word('fundamental_schools', 'escolas')
        else:
            raise Exception('Coluna "Número de estabelecimentos de ensino fundamental" fora do padrão')

    def validate_medium_schools(self):
        self.df.rename(
            columns={
                'Número de estabelecimentos de ensino médio': 'medium_schools'
            }, inplace=True)

        percent = self.count_occurrence('medium_schools', 'escolas')
        if percent == len(self.df):
            self.remove_word('medium_schools', 'escolas')
        else:
            raise Exception('Coluna "Número de estabelecimentos de ensino médio" fora do padrão')

    def validate_PIB(self):
        self.df.rename(
            columns={
                'PIB per capita': 'PIB'
            }, inplace=True)

        percent = self.count_occurrence('PIB', 'R')
        if percent == len(self.df):
            self.remove_word('PIB', 'R$', remove_coma=True)
        else:
            raise Exception('Coluna "PIB per capita" fora do padrão')

    def validate_receitas_fontes_externas(self):
        self.df.rename(
            columns={
                'Percentual das receitas oriundas de fontes externas': 'receitas_fontes_externas'
            }, inplace=True)

        percent = self.count_occurrence('receitas_fontes_externas', '%')
        if percent == len(self.df):
            self.remove_percent('receitas_fontes_externas')
        else:
            raise Exception('Coluna "Percentual das receitas oriundas de fontes externas" fora do padrão')

    def validate_population_last_census(self):
        self.df.rename(
            columns={
                'População no último censo': 'population_last_census'
            }, inplace=True)
        
        percent = self.count_occurrence('population_last_census', 'pessoas')
        if percent == len(self.df):
            self.remove_word('population_last_census', 'pessoas')
        else:
            raise Exception('Coluna "População no último censo" fora do padrão')

    def validate_demographic_density(self):
        self.df.rename(
            columns={
                'Densidade demográfica': 'demographic_density'
            }, inplace = True)
            
        percent = self.count_occurrence('demographic_density', 'hab')
        if percent == len(self.df):
            self.remove_word('demographic_density', 'hab/km²', remove_coma=True)
        else:
            out_standart = self.show_out_standard_values('demographic_density', 'hab')
            out_standart = pd.DataFrame(out_standart)

            percent = self.count_occurrence('demographic_density', 'pessoas', out_standart)
            if percent == len(out_standart):
                self.df.loc[self.df['demographic_density'].str.contains('pessoas', na=False), 'demographic_density'] = np.nan
                return self.validate_demographic_density()
            raise Exception('Coluna "Densidade demográfica" fora do padrão')

    def validate_estimated_population(self):
        self.df.rename(
            columns = {
                'População estimada': 'estimated_population'
            }, inplace=True)
        
        percent = self.count_occurrence('estimated_population', 'pessoas')
        if percent == len(self.df):
            self.remove_word('estimated_population', 'pessoas')
        else:
            out_standart = self.show_out_standard_values('estimated_population', 'pessoas')
            out_standart = pd.DataFrame(out_standart)

            percent = self.count_occurrence('estimated_population', 'sal')
            if percent == len(out_standart):
                self.df.loc[self.df['estimated_population'].str.contains('sal', na=False), 'estimated_population'] = np.nan
                return self.validate_estimated_population()
            raise Exception('Coluna "População estimada" fora do padrão')

    def validate_occupied_people(self):
        self.df.rename(
            columns = {
                'Pessoal ocupado': 'occupied_people'
            }, inplace = True)

        percent = self.count_occurrence('occupied_people', 'pessoas')
        if percent == len(self.df):
            self.remove_word('occupied_people', 'pessoas')
        else:
            out_standart = self.show_out_standard_values('occupied_people', 'pessoas')
            out_standart = pd.DataFrame(out_standart)

            percent = self.count_occurrence('occupied_people', '%')
            if percent == len(out_standart):
                self.df.loc[self.df['occupied_people'].str.contains('%', na=False), 'occupied_people'] = np.nan
                return self.validate_occupied_people()

            raise Exception('Coluna "Pessoal Ocupado" fora do padrão')
    
    def validate_average_salary(self):
        self.df.rename(
            columns = {
                'Salário médio mensal dos trabalhadores formais': 'average_salary'
            }, inplace = True)

        percent = self.count_occurrence('average_salary', 'sal')
        if percent == len(self.df):
            self.remove_word('average_salary', 'salários mínimos', remove_coma=True)
        else:
            raise Exception('Coluna "Salário médio mensal dos trabalhadores formais" fora do padrão')

    def validate_occupied_population(self):
        self.df.rename(
            columns = {
                'População ocupada': 'occupied_population'
            }, inplace = True)

        percent = self.count_occurrence('occupied_population', '%')
        if percent == len(self.df):
            self.remove_percent('occupied_population')
        else:
            raise Exception('Coluna "População ocupada" fora do padrão')

    def validate_all(self):
        # Gentílico
        self.validate_area_territorial()
        self.validate_arborizacao()
        self.validate_esgotamento()
        self.validate_urbanizacao_vias()
        self.validate_matriculas_fundamental()
        self.validate_matriculas_medio()
        self.validate_half_income()
        self.validate_ideb()
        self.validate_school_minor()
        # Total de receitas realizadas
        self.validate_estabelecimento_sus()
        # Total de despesas empenhadas
        self.validate_IDHM()
        self.validate_infant_death()
        self.validate_diarrhea_hospitalizations()
        self.validate_fundamental_teachers()
        self.validate_medium_teachers()
        self.validate_fundamental_schools()
        self.validate_medium_schools()
        self.validate_PIB()
        self.validate_receitas_fontes_externas()
        self.validate_population_last_census()
        self.validate_demographic_density()
        self.validate_estimated_population()
        self.validate_occupied_people()
        self.validate_average_salary()
        self.validate_occupied_population()

    def drop_columns(self):
        self.df.drop(['Gentílico', 'Total de receitas realizadas', 'Total de despesas empenhadas'], axis=1, inplace=True)

    def interpret(self):
        shape = self.df.shape[1]
        self.validate_all()
        self.drop_columns()
        print(f'Processing done: {(shape - 3) == self.df.shape[1]}')


path = './helper/downloaded_files/IBGE'
with open(f'{path}/ibge_cities_info.json') as f:
    data = json.load(f)

interpreter = Interpreter(data)
interpreter.interpret()
interpreter.df.to_json(f'{path}/ibge_cities_info_processed.json', orient='index')
