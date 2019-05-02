import requests
from bs4 import BeautifulSoup
import csv
import sys
from loguru import logger
import concurrent.futures

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATA_URL = 'https://phina.ran.gob.mx/lib/x_consultaPhina.php?idPhina=%s&intOpc=1'

def init_session():
    url = 'https://phina.ran.gob.mx/x_acceso.php'
    values = {'email': 'jcordoba@iadb.org',
              'pass': '93b48efe56'}
    s = requests.session()

    r = s.post(url, data=values, verify=False)
    return s

def elements():
    i = 0
    with open('nucleos.csv', encoding='latin1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            i = i + 1
            #if i > 10: return
            yield (i, row[0][:-1])

def main():
    global session
    logger.add("file_{time}.log", level="INFO", enqueue=True)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for x in executor.map(get_data, elements(), chunksize=1000):
            #print(str(x[0]) + ',' + ','.join(x[1:]))
            logger.info(','.join(x))

#    with open('nucleos.csv', encoding='latin1') as csv_file:
#        csv_reader = csv.reader(csv_file, delimiter=',')
#        i = 1
#        for row in csv_reader:
#            id = row[0][:-1]
#            result = get_data(session, id)
#            print(id + ',' + ','.join(result))
#            logger.debug("Registro {}", i)
#            i = i+1


def get_data(args):
    logger.debug("Get data for {}->{}", args[0], args[1])

    session = init_session()
    i = 0
    r = ''
    while True:
        try:
            r = session.get(DATA_URL  % (args[1]), verify=False, timeout=5)
            break
        except requests.exceptions.Timeout:
            session = init_session()
        except BaseException as error:
            logger.debug("Excepcion {}, reintentando {}", error, args[0])

    soup = BeautifulSoup(r.content, 'html.parser')

    try:
        inscripcion = soup.find(attrs={'name':'txtFecha'})['value']
        ejidatarios = soup.find(attrs={'name':'txt_AsentH2'})['value']
        avecindados = soup.find(attrs={'name':'txt_Reser2'})['value']
    except TypeError:
        logger.error("No se pudo parsear {}, {}", r, args[0])
        return (str(args[0]), args[1], '', '', '')

    logger.debug("Got data for {}: {} {} {}", args[0], inscripcion, ejidatarios, avecindados)
    return (str(args[0]), args[1], inscripcion, ejidatarios, avecindados)

if __name__=='__main__':
    main()

