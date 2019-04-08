import json
import threading
import time
import sys

from os import listdir
from os.path import isfile, join
from helper.Chrome import Chrome
from helper.Request import Request
from helper.Interpreter import Interpreter
from helper.Exporter import Exporter
from helper.Cities import Cities


class Scripts_RS:
    def __init__(self):
        with open('./helper/objects/rio_grande_do_sul_objects.json') as f:
            self.objects = json.load(f)

        self.chrome = Chrome()
        self.request = Request()
        self.cities = Cities()

    def open_driver(self, headless=True, full_screen=False):
        self.chrome.set_options(headless).get_driver(full_screen)

    def remove_duplicates(self, elements):
        result = []
        [result.append(element.get_attribute('href')) for element in elements]
        return sorted(set(result))

    def navigate_to(self):
        self.chrome.navigate(self.objects['url'])
        title = self.chrome.wait_for(obj=self.objects['indicadores_criminais'])
        if title is False:
            self.navigate_to()

    def navigate_to(self, url, title):
        self.chrome.navigate(url)
        object_found = self.chrome.wait_for(complex_obj=title)
        if object_found is False:
            self.navigate_to(url, title)

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
                pass

    def get_all_files_downloaded(self):
        path = './helper/downloaded_files/RS'
        city = [join(f'{path}/city', f)
                for f in listdir(f'{path}/city') if isfile(join(f'{path}/city', f))]
        general = [join(f'{path}/general', f)
                   for f in listdir(f'{path}/general') if isfile(join(f'{path}/general', f))]
        return city, general

    def export_files(self, files):
        interpreter = Interpreter()
        exporter = Exporter()
        for file in files:
            try:
                year, data = interpreter.interpret(file)
                exporter.export(year, data)
            except Exception as e:
                print(e)

    def files_script(self):
        # TODO: criar filas de erro para caso o processo falhe em um ponto
        #       o mesmo possa tentar dar um retry após o término.
        self.open_driver()
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
            kwargs={'files': city}).start()

        # FIXME: Interpreter para os arquivos do estado (ISSUE: #1)
        # threading.Thread(
        #     target=self.export_files,
        #     kwargs={ 'files': general }).start()

    def info_script(self):
        start = time.time()
        print("openning browser")
        self.open_driver(headless=False, full_screen=True)
        print("waiting for flag")
        self.navigate_to(
            url=self.objects['ibge']['url'], title=self.objects['ibge']['bandeira'])
        print("clicking into button")
        button = False
        while button is False:
            button = self.chrome.wait_for(
                complex_obj=self.objects['ibge']['gerar_resumo'])
        self.chrome.click(complex_obj=self.objects['ibge']['gerar_resumo'])

        print("getting all labels")
        elements = []
        while len(elements) == 0:
            elements = self.chrome.get_objects(
                complex_obj=self.objects['ibge']['labels'])
        threads_number = round(len(elements)/6)

        #TODO: 
        for i in range(6):
            print(f'clicking in labels {i} from {len(elements)}')
            elements[i].click()

        print('opening report')
        self.chrome.click(complex_obj=self.objects['ibge']['gerar_relatorio'])
        self.chrome.driver.switch_to.window(
            self.chrome.driver.window_handles[1])

        print('waiting on table to load')
        obj = False
        while obj is False:
            obj = self.chrome.wait_for(
                simple_obj=self.objects['ibge']['table']['title'])

        print('getting columns')
        columns_xpath = self.objects['ibge']['table']['columns']
        columns = self.chrome.get_objects(simple_obj=columns_xpath)
        columns_names = [name.text for name in columns]

        print('getting rows')
        rows_xpath = self.objects['ibge']['table']['rows']['tag']
        rows = self.chrome.get_objects(simple_obj=rows_xpath)
        print(f'rows retrieved {len(rows)}')

        print('getting information')
        information_xpath = self.objects['ibge']['table']['rows']['info']
        for i in range(len(rows)):
            if i % 50 == 0 or i == len(rows):
                print(f'{i} from {len(rows)}')
            info = rows[i].find_elements_by_xpath(information_xpath)
            name = info[0].text
            for z in range(1, len(info)):
                attribute_name = columns_names[z]
                attribute = info[z].text
                self.cities.update_city(name, attribute_name, attribute)

        end = time.time()
        print('time elapsed: ', end - start)

    def run(self):
        self.info_script()


script = Scripts_RS()
try:
    script.run()
finally:
    script.chrome.close()
    pass
