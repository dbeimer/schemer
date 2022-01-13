
import openpyxl
import re
import sys
import string
import datetime
import unidecode
import pandas as pd
import numpy as np

from pathlib import Path

# print(sys.argv)
# file_path=None
# if len(sys.argv)>1:
#     file_path=sys.argv[1]

chars=string.punctuation

def string_tratment(value):
    value=value.lower()
    value=unidecode.unidecode(value) #quitando Ñs y tildes
    value=re.sub(r'['+chars+']', ' ', value) #quitando caracteres especiales
    value=value.split()

    return '_'.join(value)


def generateDataType(row):
    tipos=[]

    for dato in row:
        diccionario={'sql':'varchar(100)','bq':'STRING','comment':''}
        if type(dato)==str:
            diccionario['bq']='STRING'
            if len(dato)<100:
                diccionario['sql']='varchar(50)'
            elif len(dato)<50:
                diccionario['sql']='varchar(20)'
            elif len(dato)<20:
                diccionario['sql']='varchar(10)'

        elif type(dato)==int or type(dato)==np.int64:
            if len(str(dato))>5:
                diccionario['bq']='STRING'
                diccionario['sql']='varchar(20)'
            else:
                diccionario['bq']='INTEGER'
                diccionario['sql']='int'

        elif type(dato)==float:
            diccionario['bq']='FLOAT'
            diccionario['sql']='numeric'

        elif type(dato)==datetime.datetime:
            diccionario['bq']='DATETIME'
            diccionario['sql']='datetime'
            if dato.isoformat().split('T')[1]=='00:00:00':
                diccionario['bq']='DATE'
                diccionario['sql']='date'

        elif dato==None:
            diccionario['comment']='🦊️ verificar está vacio'
        else:
            diccionario['comment']='👀️ verificar'

            print(dato)
            print(type(dato))

        tipos.append(diccionario)
    return tipos


def printSqlDataType(header,dataType):
    text='=='*5+"✏️  SQL "+"=="*5+"\n"
    for index,dato in enumerate(header):
        text=text+"{} {} null,\n".format(dato,dataType[index]['sql'])

    text=text+"{} {} null,\n".format("archivo",'varchar(100)')
    text=text+"{} {} null,\n".format("creado_el","timestamp")
    text=text+"{} {} null,\n".format("motivo_rechazo","varchar(100)")
    return text


def printBqDataType(header,dataType):
    text='=='*5+"✏️  BQ "+"=="*5+"\n"
    for index,dato in enumerate(header):
        bq_row_string='name:"{}", type:"{}", mode:"NULLABLE"'.format(dato,dataType[index]['bq'])
        text=text+"{"+bq_row_string+"},\n"

    text=text+'name:"{}", type:"{}", mode:"NULLABLE",\n'.format("archivo",'STRING')
    text=text+'name:"{}", type:"{}", mode:"NULLABLE",\n'.format("creado_el",'DATETIME')
    text=text+'name:"{}", type:"{}", mode:"NULLABLE",\n'.format("motivo_rechazo",'STRING')
    return text


def process_file(file_path):
    print("He recibido lo siguiente:{}".format(file_path))
    text=''
    file=Path(file_path)
    extension_file=file.suffix

    header=[]
    row1=[]

    # print("estension:",extension_file)

    if extension_file=='.csv':
        df=pd.read_csv(file_path)
        header=df.columns.values.tolist()
        header=[string_tratment(x) for x in header]
        row1=df.iloc[0].values.tolist()

    elif extension_file=='.xlsx' or extension_file=='.xls':
        wb_obj=openpyxl.load_workbook(file)
        sheet=wb_obj.active
        header=[string_tratment(row.value) for row in sheet[1] if row.value!=None]
        row1=[row.value for row in sheet[2]]

    elif extension_file=='.txt':
        with open(file_path,'r') as f:
            text=f.read()
            text.split('\n')
            #identfy separator
            return "This filetype is still in development!!!"


    else:
        return "This filetype is not supported yet!!!"


    tipos=generateDataType(row1)

    text=printSqlDataType(header,tipos)
    text=text+"\n"

    text=text+printBqDataType(header,tipos)
    text=text+"\n"

    text=text+'=='*5+"✏️  rows "+"=="*5+"\n"
    for index,dato in enumerate(header):
        text=text+"{},\n".format(dato)
    text=text+"\n"

    text=text+'=='*5+"✏️  obj creation "+"=="*5+"\n"
    for index,dato in enumerate(header):
        text=text+"{}:row.{},\n".format(dato,dato)

    return text

