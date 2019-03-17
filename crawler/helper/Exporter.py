import json
import pyrebase
import pandas as pd
from Interpreter import Interpreter

class Exporter:
    def __init__(self):
        with open('./crawler/helper/firebase/pyrebase_config.json') as f:
            config = json.load(f)

        self.db = pyrebase.initialize_app(config).database()

    def export(self, year, data_frame):
        df_as_json = data_frame.to_json(orient='index', force_ascii=False)
        json_objects = json.loads(df_as_json)

        for key in json_objects:
            raw_value = json_objects[key]
            value = { year : raw_value }
            # TODO: validar se a cidade já existe (ver read_test):
            #   1- Se existe atualizar registro com o ano em questão (update)
            #   self.db.child("rio_grande_do_sul").child(key).update(value)
            #   2- Se não existe criar registro com própria chave (set)
            #   self.db.child("rio_grande_do_sul").child(key).set(value)

    
    def read_test(self):
        test = self.db.child('rio_grande_do_sul').child('ACEGUA').get()
        print(test.val())

interpreter = Interpreter()
year, data = interpreter.interpret('./crawler/helper/downloaded_files/RS/city/04151117-31164413-indicadores-criminais-ssp-por-municipio-2003.xls')
exporter = Exporter()
exporter.export(year, data)
# exporter.read_test()
