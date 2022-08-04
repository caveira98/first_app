####################################### Aquisição de dados
#import basics
import streamlit as st 
import requests
import pandas as pd
import numpy as np
from functools import reduce
#expericing library

import plotly.graph_objects as go
from datetime import date
#data sources
import openpyxl
import datetime as dt
import base64
import io
#feito para traduzir o nome dos gráficos 


#gerando funcoes para a aplicação 
def get_covid_data():
    """funcao para baixar os dados de covid
    in:  nada
    out: dataframe
    """
    url='https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
    df= pd.read_csv(url, sep=',')
    return df

def get_table_download_link(df, nome):
    """Gera link para baixar os dados selecionados
    in:  dataframe, nome do arquivo
    out: href string
    """
    towrite = io.BytesIO()
    downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()  # some strings
    linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{nome}_{date.today()}.xlsx">Click aqui para baixar os seus dados</a>'
    return linko


def download_link(object_to_download, download_filename, download_link_text):
    """Gera link para baixar os dados selecionados

    in:  dataframe, nome do arquivo, nome do link do arquivo
    out: href string
    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False,decimal= ",")

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{nome}_{date.today()}.csv">{download_link_text}</a>'

def grafico(df):
    fig = go.Figure()
    colors = [ '#0A3254', '#7AADD4', '#B2292E','#336094', '#E0D253','#0A3264', '#8AADD4', '#B2290E','#339094', '#E0D353']

    for i in range(len(df.columns)):
        fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:, i], line=dict(color=colors[i], width=2.25), name=df.columns[i]))
    
    fig.update_layout(template='plotly_dark',
                             font_family="Verdana", 
                             legend=dict(
                                 orientation="h",
                                 yanchor="bottom",
                                 y=1.05,
                                 xanchor="center",
                                 x=0.5,
                                 font_family='Verdana'),
                                 autosize=False, height= 550, width=750
                                 )

    return fig , df.reset_index()

#Montando o Apllicativo
df = get_covid_data()

#frontend
st.title('Uma aplicação  para simplificar o processo de extração de dados por país da pandemia')

#gerando seção para escolher as variaveis iniciais
with st.expander("⚙️ Configure as Opções"):
    loc_list = df['location'].drop_duplicates()
    loc_select = st.multiselect('select country',loc_list, default=["Brazil"])
    var_list = df.columns.to_list()
    var_select = st.multiselect('select var',var_list,default=["new_cases_smoothed"])
    nome =  var_select[0]
    data =df[df['location'].isin(loc_select)]
    #data.location = data['location'].apply(translator.translate, src='ing', dest='port').apply(getattr, args=('text',))
    #data['location'] = GoogleTranslator(source='en', target='pt').translate(data['location'])
    data = data[['location', 'date', var_select[0]]]
    data = data.pivot_table(index='date',columns='location', values=var_select[0])

#mostrando para o usuário os dados que ele escolheu como uma tabela e também comouma figura
st.write('tabela inicials')
st.write(df.head())

#gerando e plotando a figura, também fiz um leve ajuste para deixar resetar o index dos dados 
figura, data = grafico(data)
st.plotly_chart(figura,use_container_width=True) 

#gerando os botoes de dados 
col1, col2 = st.columns(2)
#deixando os botões lado a lado
with col1:
    if st.button('Download Dataframe como um CSV'):
        csv_link = download_link(data, '{nome}.csv', 'Click aqui para baixar os seus dados')
        st.markdown(csv_link, unsafe_allow_html=True)

with col2:
    if st.button('Download Dataframe como um Excel'):
        excel_link= get_table_download_link(data, nome)
        st.markdown(excel_link , unsafe_allow_html=True)