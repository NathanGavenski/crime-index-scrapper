import json
import pyrebase
import unidecode
import pandas as pd

class Exporter:
    # TODO Delete all files after it send to firebase real time database
    def __init__(self):
        with open('./helper/firebase/pyrebase_config.json') as f:
            config = json.load(f)

        self.cities_list = []
        self.db = pyrebase.initialize_app(config).database()
        self.cities = self.db.child('rio_grande_do_sul').get()

    def export(self, year, data_frame):
        df_as_json = data_frame.to_json(orient='index', force_ascii=False)
        json_objects = json.loads(df_as_json)

        for key in json_objects:
            raw_value = json_objects[key]
            value = { year : raw_value }
            if key == 'Total RS':
                if self.check_if_exist(key) is False:
                    print(f'Creating for the first time register for {key} on year {year}')
                    self.db.child("rio_grande_do_sul").child(key).set(value)
                else:
                    print(f'Updating registry {key} for year {year}')
                    self.db.child("rio_grande_do_sul").child(key).update(value)

    def export_ibge(self, data):
        if isinstance(data, dict) is False:
            raise Exception('Wrong class type, data should be "dict"')

        cities_list = self.get_cities_list()
        for key in data:
            city_name = self.clear_name(key)
            if city_name in cities_list:
            else:
                print(f'Cidade {city_name} não está na base')

    def get_cities_list(self):
        if len(self.cities_list) > 0:
            return self.cities_list
   
        for city in self.cities.each():
            self.cities_list.append(city.key())
        
        return self.cities_list

    def clear_name(self, city_name):
        name = unidecode.unidecode(city_name.upper())
        name = name.replace('\'', '')
        name = name.replace('ENTRE-', 'ENTRE ')
        name = name.replace('VILANOVA', 'VILA NOVA')
        return name
        

    def check_if_exist(self, city_name):
        if city_name in self.get_cities_list():
            return True
        return False

    
path = './helper/downloaded_files/IBGE'
with open(f'{path}/ibge_cities_info_processed.json') as f:
    data = json.load(f)

exporter = Exporter()
exporter.export_ibge(data)