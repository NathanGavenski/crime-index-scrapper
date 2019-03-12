import re
import pandas as pd


class Interpreter:
    def __init__(self):
        self.older_version_regex = r'em \d{4} \(Totalização\)'
        self.newer_version_regex = r'de 01 de janeiro à 31 de dezembro de \d{4}'
        self.current_version_regex = r'no período de 01 de janeiro a'

    def interpret(self, file):
        self.file = pd.ExcelFile(file)
            
        df = pd.read_excel(file)
        if 'municipio' in file:
            self.old_type = self.define_city_version(df)
            year = self.define_year(df, True)
            df = self.parse_city_data(df)
        else:
            self.old_type = self.define_general_version(df)
            year = self.define_year(df, False)
            df = self.parse_general_data(df)
        return year, df

    def define_year(self, df, municipio):
        year_regex = r'\d{4}'
        year_text = self.get_year_text(df, municipio)
        year = re.search(year_regex, year_text)
        return year.group(0)

    def get_year_text(self, df, municipio):
        if municipio is True:
            if self.old_type == '2011':
                year_text = self.file.sheet_names[0]
            elif self.old_type == '2019':
                year_text = df.iloc[2,0]
            else:
                year_text = df.iloc[3, 0]
        else:
            year_text = df.iloc[2,1] if self.old_type is True else df.iloc[2,0]
        return year_text


    def define_city_version(self, df):
        year_text = df.iloc[3, 0]
        try:
            if re.compile(self.older_version_regex).search(year_text):
                return 'older'
            elif re.compile(self.newer_version_regex).search(year_text):
                return 'newer'
        except TypeError:
            if re.compile(self.current_version_regex).search(df.iloc[2,0]):
                return '2019'

        if '2011' in self.file.sheet_names:
            return '2011'
        else:
            raise Exception(f'Didn\'t match any version known for the file: {self.file}')

    def define_general_version(self, df):
        axis_x, _ = df.shape
        if axis_x < 20:
            return True
        elif axis_x < 50:
            return False
        else:
            raise Exception(f'Didn\'t match any version known for the file: {self.file}')

    def parse_city_data(self, df):
        if self.old_type is 'older':
            df.columns = df.iloc[5].values
            df = df.drop(range(6), axis=0)
            return df.drop([df.index[-1], df.index[-2]], axis=0)
        elif self.old_type is 'newer':
            df.columns = df.iloc[10].values
            df = df.drop(range(11), axis=0)
            return df.drop(range(df.index[-10], df.index[-1] + 1), axis=0)
        elif self.old_type is '2011':
            df.columns = df.iloc[0].values
            df = df.drop(0, axis=0)
            return df.drop(df.index[-1], axis=0)
        elif self.old_type is '2019':
            print(self.file.sheet_names)

    def parse_general_data(self, df):
        if self.old_type is True:
            df.columns = df.iloc[4].values
            df = df.drop(range(5), axis=0)
            df = df.drop(df.index[-1], axis=0)
            return df.dropna(axis=1, how='all')
        elif self.old_type is False:
            df.columns = df.iloc[4].values
            df = df.drop(range(5), axis=0)
            df = df.drop(range(df.index[-31], df.index[-1] + 1), axis=0)
            return df.dropna(axis=1, how='all')

file_2019 = './crawler/helper/downloaded_files/RS/city/12095700-site-municipios-janeiro.xlsx'
file_2002 = './crawler/helper/downloaded_files/RS/city/04145411-31164405-indicadores-criminais-ssp-por-municipio-2002.xls'
file_2018 = './crawler/helper/downloaded_files/RS/city/11174440-site-municipios-2018.xlsx'
file_2011 = './crawler/helper/downloaded_files/RS/city/04154946-31164429-indicadores-criminais-ssp-por-municipio-2011-por-mes.xls'
interpreter = Interpreter()
print(interpreter.interpret(file_2019))
