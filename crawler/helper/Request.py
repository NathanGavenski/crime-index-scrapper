import requests, os


class Request:

    def __init__(self):
        self.file_path = './helper/downloaded_files/'
        self.accepted_formats = (
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel'
        )

    def is_downloadable(self, url):
        h = requests.head(url, allow_redirects=True)
        return True if h.headers.get('content-type') in self.accepted_formats else False

    def download_file(self, url, state, index_type):
        print('downloading: ', url)
        r = requests.get(url, allow_redirects=True)
        name = url.split('/')[-1]
        path = f'{self.file_path}/{state}/{index_type}'
            
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except IOError as excepion:
            print('Problem creating directory: ', str(excepion))

        try:
            open(f'{path}/{name}', 'wb').write(r.content)
            return True
        except IOError as excepion:
            print('Problem saving file: ', str(excepion))
            return False