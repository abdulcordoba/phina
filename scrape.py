import sys
import requests
from bs4 import BeautifulSoup
import csv
from loguru import logger
import concurrent.futures
from random import random
import time

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATA_URL = 'https://phina.ran.gob.mx/lib/x_consultaPhina.php?idPhina=%s&intOpc=1'

# Crear sesión autenticada (puede causar excepción, ni modo!)
def init_session(timeout=3):
    url = 'https://phina.ran.gob.mx/x_acceso.php'
    values = {'email': 'jcordoba@iadb.org',
              'pass': '93b48efe56'}
    s = requests.session()

    r = s.post(url, data=values, verify=False, timeout=timeout)
    logger.debug("Create session: {}", r.text)

    return s

# ids desde el archivo como generador    
def elements(fin):
    i = 0
    with open(fin, encoding='latin1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            i = i + 1
            #if i > 10: return
            yield (i, row[0][:-1])

# Crear sesión inicial y mandar al pool!
def main(fin):
    logger.add("file_%s.log" % (sys.argv[1]))

    s = init_session()
    f = make_get(s)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for x in executor.map(f, elements(fin)):
            pass

# Encapsular session inicial (overkill)
def make_get(session):
    return lambda args: get_data(session, args)

# Hacer el request y parsear
def get_data(session, args):
    # why TCP why!!!
    time.sleep(random()*4)
    logger.debug("Get data for {}->{}", args[0], args[1])

    r = ''
    while True:
        try:
            # happy path
            r = session.get(DATA_URL  % (args[1]), verify=False, timeout=15)
            break
        except requests.exceptions.Timeout:
            # reintentar con sesión nueva
            session = init_session()
        except BaseException as error:
            # whatever...
            logger.debug("Excepcion {}, reintentando {}", error, args[0])

    soup = BeautifulSoup(r.content, 'html.parser')

    try:
        inscripcion = soup.find(attrs={'name':'txtFecha'})['value']
        ejidatarios = soup.find(attrs={'name':'txt_Parcelada2'})['value']
        avecindados = soup.find(attrs={'name':'txt_Reser2'})['value']
    except TypeError:
        # wanna cry :,(
        logger.error("No se pudo parsear {}, {}", r.text, args[0])
        return (str(args[0]), args[1], '', '', '')

    logger.debug("Got data for {}: {} {} {}", args[0], inscripcion, ejidatarios, avecindados)
    # This is what I will actually filter 
    logger.info(','.join((str(args[0]), args[1], inscripcion, ejidatarios, avecindados)) )
    # This value is just ignored
    return (str(args[0]), args[1], inscripcion, ejidatarios, avecindados)

if __name__=='__main__':
    # param is name of file (broken big file)
    main(sys.argv[1])

