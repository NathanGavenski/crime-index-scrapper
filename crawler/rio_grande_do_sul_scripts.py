import json
import threading

from os import listdir
from os.path import isfile, join
from helper.Chrome import Chrome
from helper.Request import Request
from helper.Interpreter import Interpreter

class Scripts_RS:
    def __init__(self):
        with open('./crawler/objects/rio_grande_do_sul_objects.json') as f:
            self.objects = json.load(f)

        self.chrome = Chrome()
        self.chrome.set_options().get_driver(full_screen=False)

        self.request = Request()

    def remove_duplicates(self, elements):
        result = []
        [result.append(element.get_attribute('href')) for element in elements]
        return sorted(set(result))

    def navigate_to(self):
        self.chrome.navigate(self.objects['url'])
        title = self.chrome.wait_for(obj=self.objects['indicadores_criminais'])
        if title is False:
            self.navigate_to()

    def get_general_crime_indices(self):
        try:
            indicador_geral = self.objects['indicador_geral']
            elements = self.chrome.get_objects(xpath=indicador_geral['xpath'])
            return self.remove_duplicates(elements)
        except Exception as exception:
            print('Exception: ', exception)

    def get_by_city_crime_indices(self):
        try:
            indicador_municipio = self.objects['indicador_por_municipio']
            elements = self.chrome.get_objects(obj=indicador_municipio)
            return self.remove_duplicates(elements)
        except Exception as exception:
            print('Exception: ', exception)

    def get_files(self):
        self.navigate_to()
        city_urls = self.get_by_city_crime_indices()
        general_urls = self.get_general_crime_indices()
        return city_urls, general_urls

    def download_files(self, urls, index_type):
        for url in urls:
            if self.request.is_downloadable(url):
                self.request.download_file(url, 'RS', index_type)
            else:
                print(f'{url} not an excel file type')

    def get_all_files_downloaded(self):
        path = './crawler/helper/downloaded_files/RS'
        city = [join(f'{path}/city', f) for f in listdir(f'{path}/city') if isfile(join(f'{path}/city', f))]
        general = [join(f'{path}/general', f) for f in listdir(f'{path}/general') if isfile(join(f'{path}/general', f))]
        return city, general

    def export_files(self, files):
        interpreter = Interpreter()
        for file in files:
            try:
                year, data = interpreter.interpret(file)
                print(file.split('/')[-1], year)
            except Exception as e:
                print(e)

    def run(self):
        city, general = self.get_files()
        self.chrome.close()

        t1 = threading.Thread(
                target=self.download_files,
                kwargs={
                    'urls': city,
                    'index_type': 'city'
                })
        t1.start()

        t2 = threading.Thread(
                target=self.download_files,
                kwargs={
                    'urls': general,
                    'index_type': 'general'
                })
        t2.start()

        t1.join()
        t2.join()

        city, general = self.get_all_files_downloaded()
        threading.Thread(
            target=self.export_files,
            kwargs={ 'files': city }).start()

        threading.Thread(
            target=self.export_files,
            kwargs={ 'files': general }).start()


script = Scripts_RS()
script.run()
