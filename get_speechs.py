import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import locale
from datetime import datetime 
from tqdm import tqdm
from userAgents import randomUserAgents
import urllib3

urllib3.disable_warnings()
locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
head = randomUserAgents()

def bs(url,headers):
    ''' url = casarisada.gob.ar/informacion/discursos '''
    session = requests.Session()
    req = session.get(url, headers=headers, verify = False)
    bs = BeautifulSoup(req.text, 'html.parser')
    return bs

def collect_speech_urls(speech_list, soup):
    '''In this step we collect all the presidential speeches urls available in the site of casarosada'''
    i = 1
    try:
        while True:
            speeches = soup.find_all("a", {"class": "panel"}, href=True)
            speech_list.extend([text['href'] for text in speeches])      
            next_page = soup.find("li", {"class": "pagination-next"}).find("a")['href']
            next_page_url = urljoin(url, next_page)
            soup = bs(next_page_url, head)
            i += 1
            print(f"going to page {i}")
    except TypeError:
        print("end of page reached")

def obtain_speech_text(speech_list, soup):
    '''In this step we collect all the presidential speeches from the urls obtained in the step before'''
    for speech_url in tqdm(speech_list):
        get_url = urljoin(url, speech_url)
        head = randomUserAgents()
        soup = bs(get_url, head)
        title = soup.find("h2").text
        date_string = soup.find("time", {"class": "pull-right"}).text.strip()
        try:
            date = datetime.strptime(date_string, '%A %d de %B de %Y')
        except ValueError:
            date = datetime(1990,1,1)
        body = soup.find("article").text.strip()
        presidential_speech.append((speech_url, title, date, body))

def run():
    url = "https://www.casarosada.gob.ar/informacion/discursos"
    soup = bs(url, head)
    speech_list = []

    collect_speech_urls(speech_list, soup)

    presidential_speech = []
    obtain_speech_text(speech_list, soup)

    df = pd.DataFrame(presidential_speech, columns=["speech_url", "title", "date", "body"])
    df.to_csv("presidential_speeches.csv", index=False)

if __name__ == '__main__':
    run()