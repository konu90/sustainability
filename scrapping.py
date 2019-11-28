
# coding: utf-8

# In[17]:


#Libreria para aplicar funciones reges
import re
#Libreria para obtener el html de una url
from urllib.request import urlopen
#Libreria para webscrapping
from bs4 import BeautifulSoup
#Permite generar random enteros
from random import randint
#Modulo para tareas de tiempo
import time
import os
import pandas as pd
import numpy as np


# In[18]:


#Metodo que con funciones regex obtiene los datos de las tablas pvoutput
def extraeInfoWeb (webscrap): 
    auxInput = []

    # Obtén fecha
    regex = "dt=.\d*\"\>(\d\d\/\d\d\/\d\d|-)"
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)

    # Obtén energía generada (Generated)
    regex = "title=\"Exported: None\">(\d*\.\d*|-)"
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)

    # Obtén eficiencia (efficiency)
    regex = "style=\"padding-right:25px\">(.d*\.\d*|-)"
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)

    # Obtén pico de potencia (peak power)
    regex = "style=\"padding-right:35px\">(\d*\.\d*|-)"
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)

    # Obtén hora de pico (peak time)
    regex = "<td align=\"center\">(\d*\:\d*..|-)"
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)

    # Obtén tipo de día (condictions)
    regex = "<td nowrap=\"\">(\w*\s\w*|\w*|-)</td><td align=\"right\""
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)


    datosBruto = np.array(auxInput).T.tolist()
    enpandas = pd.DataFrame(datosBruto)
    return enpandas


# In[19]:


#Construimos las URLS a las que vamos a pedir información
def crearUrls(anyoInicio,anyoFin,ide,sid):
    #Creamos una lista(fechaInicio) para crear la fecha de inicio de los rangos de fechas de las que se van a pedir datos
    fechaInicio = []
    for anyo in range (anyoInicio,anyoFin+1):
        for mes in range (1,13):
            if(mes <= 9):
                fecha = str(anyo)+"0"+str(mes)+"01"
            else:
                fecha = str(anyo)+str(mes)+"01"
            fechaInicio.append(fecha)

    #Creamos una lista(fechaFin) para crear la fecha de fin de los rangos de fechas de las que se van a pedir datos     
    fechaFin = []
    for anyo in range (anyoInicio,anyoFin+1):
        for mes in range (1,13):
            #Añadir el 0 a la fecha
            if(mes <= 9):
                fecha = str(anyo)+"0"+str(mes)
            else:
                fecha = str(anyo)+str(mes)
            #Comprobar si es bisiesto
            if(mes == 2):
                if(anyo%4 == 0 and anyo%100 != 0 or anyo%400 == 0):
                    fecha = fecha + "29"
                else:
                    fecha = fecha + "28"
            elif(mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes==12 ):
                fecha = fecha+"31"
            else:
                fecha = fecha+"30"
            fechaFin.append(fecha)

    #Creamos la lista fechaAux, para el primer dia de cada mes de los meses que tienen 31 dias,
    #ya que por limitaciones de la web, se muestran maximo 30 registros
    fechaAux = []
    for anyo in range (anyoInicio,anyoFin+1):
        for mes in range (1,13):
            #Si el mes tiene 31 dias...
            if(mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes==12):
                #Añadir el 0 a la fecha
                if(mes <= 9):
                    fecha = str(anyo)+"0"+str(mes) + "01"
                else:
                    fecha = str(anyo)+str(mes) + "01"
                fechaAux.append(fecha)

    #Lista de urls construidas para pedir la informacion
    #Todas las fechas
    urls = []
    for i in range (0, len(fechaInicio)):
        urls.append("https://pvoutput.org/list.jsp?df=" +str(fechaInicio[i]) + "&dt=" + str(fechaFin[i]) + "&id=" + str(ide) +"&sid=" + str(sid) + "&t=y&v=0")
    #Para los meses de 31 dias, creamos urls que piden unicamente el primer dia de ese mes
    for i in range(0,len(fechaAux)):
        urls.append("https://pvoutput.org/list.jsp?df=" +str(fechaAux[i]) + "&dt=" + str(fechaAux[i]) + "&id=" + str(ide) +"&sid=" + str(sid) + "&t=y&v=0")
    
    return urls


# In[20]:


def getData(anyoInicio,anyoFin,ide,sid):#listaUrls):
    #Creamos lista de urls a las que le vamos a pedir informacion
    urls = crearUrls(anyoInicio,anyoFin,ide,sid)
    print("Numero de urls:", len(urls))
    
#     urls = []
#     urls.append("https://pvoutput.org/list.jsp?df=20180701&dt=20180731&id=37639&sid=34434&t=y&v=0")
    #Creamos dataframe con el formato
    #nombre de las columnas
    head = ['date', "generated", "efficiency", "peakpower","peaktime","conditions"]
    df = pd.DataFrame(columns=head)
    nPeticion = 1
    #Para cada url
    for i in urls:
        print("Petición:", nPeticion)
        nPeticion  = nPeticion + 1
        url = i
        #Obtenemos el html de la web
        html = urlopen(url)
        #convertimos a lxml
        soup = BeautifulSoup(html, 'lxml')
        #Extraemos las tablas de dicha web
        tables = soup.find_all('table')
        #Obtenemos todos los parrafos de la tabla que nos interesa(tables[1])
        paragraphs = []
        for x in tables[1]:
            paragraphs.append(str(x))
        #Obtenemos el codigo html de las tuplas de la tabla(eliminamos cabecera de la tabla, etc)
        dataToParsed = []
        for x in range(2,len(paragraphs)):
            dataToParsed.append(str(paragraphs[x]))

        #Aplicamos regex para obtener los datos
        df = df.append(extraeInfoWeb(str(dataToParsed)))
        #Esperamos entre 1 y 10 segundos para hacer la siguiente peticion
        t = randint(60, 80)
        print("Tiempo de espera hasta la siguiente petición:",t)
        time.sleep(t)
    
    return df


# In[7]:


# #Parameters para la instalación del mercado del carmel en Barcelona
# #Nombre de la instalacion fotovoltaica
# name = "Mercat del carmel"
# #Anyo de inicio desde el cual queremos extraer datos
# anyoInicio = 2016
# #Anyo de fin hasta el que queremos extraer datos
# anyoFin = 2018
# #ID del sistema
# ide = 37639
# #SID del sistema
# sid = 34434
# path = os.getcwd() + "\\data\\" + name + ".csv"

# # #Get Data
# # df = getData(anyoInicio,anyoFin,ide,sid)
# # #Export to csv
# # df.to_csv(path, sep =';', index=False)


# In[21]:


#Cargamos los datos de las instalaciones de las que queremos extraer datos
pathInstalaciones = os.getcwd() + "\\data\\" + "candidatosCURL.csv"
instalaciones = pd.read_csv(pathInstalaciones, delimiter=';')
head = ['date', "generated", "efficiency", "peakpower","peaktime","conditions", "nombre", "id", "sid","potenciaInstalada","eficienciaPlaca","modeloPlaca"]
dfFinal = pd.DataFrame(columns=head)

for i in range (0,len(instalaciones)):
    #Build path
    path = os.getcwd() + "\\data\\" + instalaciones.iloc[i]['nombre instalacion'] + ".csv"
    #Nombre de la instalacion fotovoltaica
    name = instalaciones.iloc[i]['nombre instalacion']
    #Anyo de inicio desde el cual queremos extraer datos
    anyoInicio = instalaciones.iloc[i]['Anyo Inicio']
    #Anyo de fin hasta el que queremos extraer datos
    anyoFin = instalaciones.iloc[i]['Anyo Fin']
    # #ID del sistema
    ide = instalaciones.iloc[i]['Id']
    # #SID del sistema
    sid = instalaciones.iloc[i]['Sid']
    print("Instalación:", instalaciones.iloc[i]['nombre instalacion'])
    #Get Data
    df = getData(anyoInicio,anyoFin,ide,sid)
    df["nombre"] = instalaciones.iloc[i]['nombre instalacion']
    df["id"] = ide
    df["sid"] = sid
    df["potenciaInstalada"] = instalaciones.iloc[i]['Potencia Instalada']
    df["eficiencia"] = instalaciones.iloc[i]['Eficiencia Placa (%)']
    df["modeloPlaca"] = instalaciones.iloc["modeloPlaca"]
    #Export data of a instalation to csv
    df.to_csv(path, sep =';', index=False)
    dfFinal.append(df)

pathAll = os.getcwd() + "\\data\\" + "pvoutput.csv"
dfFinal.to_csv(pathAll, sep =';', index=False) 


# In[29]:


urls = crearUrls(anyoInicio,anyoFin,ide,sid)
print(urls[10])
url = urls[10]
#Obtenemos el html de la web
html = urlopen(url)
#convertimos a lxml
soup = BeautifulSoup(html, 'lxml')
#Extraemos las tablas de dicha web
tables = soup.find_all('table')
#Obtenemos todos los parrafos de la tabla que nos interesa(tables[1])
paragraphs = []
for x in tables[1]:
    paragraphs.append(str(x))
#Obtenemos el codigo html de las tuplas de la tabla(eliminamos cabecera de la tabla, etc)
dataToParsed = []
for x in range(2,len(paragraphs)):
    dataToParsed.append(str(paragraphs[x]))

dataToParsed


# In[30]:


test = extraeInfoWeb(str(dataToParsed))
test


# In[31]:


urls = crearUrls(anyoInicio,anyoFin,ide,sid)
print(urls[11])
url = urls[11]
#Obtenemos el html de la web
html = urlopen(url)
#convertimos a lxml
soup = BeautifulSoup(html, 'lxml')
#Extraemos las tablas de dicha web
tables = soup.find_all('table')
#Obtenemos todos los parrafos de la tabla que nos interesa(tables[1])
paragraphs = []
for x in tables[1]:
    paragraphs.append(str(x))
#Obtenemos el codigo html de las tuplas de la tabla(eliminamos cabecera de la tabla, etc)
dataToParsed = []
for x in range(2,len(paragraphs)):
    dataToParsed.append(str(paragraphs[x]))

dataToParsed


# In[32]:


test = extraeInfoWeb(str(dataToParsed))
test

