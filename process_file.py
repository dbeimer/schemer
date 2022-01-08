
import openpyxl
import re
import sys
import string
import datetime
import unidecode

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

def process_file(file_path):
    print("He recibido lo siguiente:{}".format(file_path))
    text=''

    file=Path(file_path)
    wb_obj=openpyxl.load_workbook(file)
    sheet=wb_obj.active
    header=[string_tratment(row.value) for row in sheet[1] if row.value!=None]

    column1=[row.value for row in sheet[2]]
    tipos=[]

    for dato in column1:
        diccionario={'sql':'varchar(100)','bq':'STRING','comment':''}
        if type(dato)==str:
            diccionario['bq']='STRING'
            if len(dato)<100:
                diccionario['sql']='varchar(50)'
            elif len(dato)<50:
                diccionario['sql']='varchar(20)'
            elif len(dato)<20:
                diccionario['sql']='varchar(10)'

        elif type(dato)==int:
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
            print(type(dato))

        tipos.append(diccionario)

    text='=='*5+"✏️  SQL "+"=="*5+"\n"
    for index,dato in enumerate(header):
        text=text+"{} {} null,\n".format(dato,tipos[index]['sql'])

    text=text+"{} {} null,\n".format("archivo",'varchar(100)')
    text=text+"{} {} null,\n".format("creado_el","timestamp")
    text=text+"{} {} null,\n".format("motivo_rechazo","varchar(100)")


#generatong schema
    text=text+"\n"
    text=text+'=='*5+"✏️  BQ "+"=="*5+"\n"
    for index,dato in enumerate(header):
        bq_row_string='name:"{}", type:"{}", mode:"NULLABLE"'.format(dato,tipos[index]['bq'])
        text=text+"{"+bq_row_string+"},\n"

    text=text+'name:"{}", type:"{}", mode:"NULLABLE",\n'.format("archivo",'STRING')
    text=text+'name:"{}", type:"{}", mode:"NULLABLE",\n'.format("creado_el",'DATETIME')
    text=text+'name:"{}", type:"{}", mode:"NULLABLE",\n'.format("motivo_rechazo",'STRING')

    text=text+"\n"
    text=text+'=='*5+"✏️  rows "+"=="*5+"\n"

    for index,dato in enumerate(header):
        text=text+"{},\n".format(dato)

    text=text+"\n"
    text=text+'=='*5+"✏️  obj creation "+"=="*5+"\n"

    for index,dato in enumerate(header):
        text=text+"{}:row.{},\n".format(dato,dato)

    return text

