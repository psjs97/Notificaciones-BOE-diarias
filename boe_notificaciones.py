#!/usr/bin/python

# Libraries
import requests, csv
from datetime import datetime
import xmltodict
import pandas as pd

print('### OBTENCIÓN NUEVAS NOTIFICACIONES BOE ###')
print("Fecha ejecución: %s" % datetime.now())

# Función para obtener fecha del día actual
def get_current_date():
    current_year = str(datetime.now().year).zfill(4)
    current_month = str(datetime.now().month).zfill(2)
    current_day = str(datetime.now().day).zfill(2)
    current_date = f'{str(current_year)}{str(current_month)}{str(current_day)}'
    return current_date
    
# Función para parsear web del BOE
def parse_current_date_xml_boe(current_date):
    xml_boe_url = f'https://www.boe.es/diario_boe/xml.php?id=BOE-S-{current_date}'
    response = requests.get(xml_boe_url)
    xml_boe_data = xmltodict.parse(response.text)

    current_date_boe_df = []

    if not 'error' in xml_boe_data.keys():
        publications = xml_boe_data['sumario']['diario']['seccion'][0]['departamento']
        if type(publications) is list:
            for publication in publications:
                if not type(publication['epigrafe']) is list:
                    publication_df = pd.json_normalize(publication, max_level = 5)
                    current_date_boe_df.append(publication_df)
                else:
                    name = publication['@nombre']
                    for i in publication['epigrafe']:
                        publication_df = pd.json_normalize(i, max_level = 5)
                        publication_df.rename(columns = {'@nombre':'epigrafe.@nombre'}, inplace = True)
                        publication_df.insert(loc=0, column='@nombre', value=name)
                        current_date_boe_df.append(publication_df)
        else:
            if not type(publications['epigrafe']) is list:
                publication_df = pd.json_normalize(publications, max_level = 5)
                current_date_boe_df.append(publication_df)
            else:
                name = publications['@nombre']
                for i in publications['epigrafe']:
                    publication_df = pd.json_normalize(i, max_level = 5)
                    publication_df.rename(columns = {'@nombre':'epigrafe.@nombre'}, inplace = True)
                    publication_df.insert(loc=0, column='@nombre', value=name)
                    current_date_boe_df.append(publication_df)
    else:
        return []
                    
    return current_date_boe_df
    
    
# Main
current_date = get_current_date()
current_date_boe_df = parse_current_date_xml_boe(current_date)
    
if len(current_date_boe_df) > 0:
    current_date_boe_df = current_date_boe_df[current_date_boe_df['DEPARTAMENTO'].str.contains("MINISTERIO DEL INTERIOR")] # Filtramos por 'Ministerio del Interior'
    current_date_boe_df.to_csv('boe_notifications_' + current_date + '.csv',sep=';',index=None) # Escritura resultados
    print('Encontradas notificaciones. Escribiendo salida en ',output_file)
else:
    print('No se han encontrado nuevas notificaciones para el día de hoy')